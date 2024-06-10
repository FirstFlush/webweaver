from __future__ import annotations
import aiodns
import aiohttp
from aiohttp.client_exceptions import ClientHttpProxyError, ClientPayloadError
import asyncio
import logging
import os
from pathlib import Path
import random
import requests
from typing import Any, TYPE_CHECKING
import ua_generator
import time
import validators

from playwright.async_api._generated import (
    Playwright as AsyncPlaywright, 
    Browser, 
    BrowserContext
)
from typing import Optional
from urllib.parse import urlparse


from webweaver.common.enums import LogLevel
from webweaver.exceptions import (
    WebScrapingError, 
    BadMarkupError, 
    SpiderHttpError, 
    ElementNotFound,
    SpiderSoupError
)
from webweaver.config import PROXY, SENTINEL
from webweaver.webscraping.spiders.spider_fuzzer import SpiderFuzzer
from webweaver.webscraping.spiders.spider_regex import SpiderRegex
from webweaver.webscraping.spiders.soup_base import SpiderSoup
from webweaver.webscraping.spiders.spider_page import SpiderPage, SpiderContext, RequestContext, RequestContextInterface
from webweaver.webscraping.middleware.middleware_manager import SpiderMiddlewareManagerInterface
from webweaver.webscraping.proxy.proxy_base import ProxySession
from webweaver.webscraping.proxy.proxy_manager import SpiderProxyManagerInterface
from webweaver.webscraping.registry.scraping_registry import scraping_registry, SpiderState
if TYPE_CHECKING:
    from webweaver.webscraping.spiders.models import SpiderAsset
    from webweaver.webscraping.spiders.soup_base import SpiderTag


logger = logging.getLogger('scraping')



class SpiderInterface:
    """Currently this class exists as a way for another class to access 
    the spider's module-level logging functionality.
    
    It maybe should be called SpiderLoggingInterface but I might add more 
    functionality to it.
    """
    def __init__(self, spider:Spider):
        self.spider = spider

    def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR):
        return self.spider.log(e, level)

    async def call_middleware(self, response:Any, request_interface:RequestContextInterface=None):
        await self.spider.middleware_manager_interface.handle_response(
            response=response, 
            spider_interface=self,
            request_interface=request_interface
        )




class SpiderModuleLog:
    """Module-level logging for a specific spider's webscraping errors"""
    def __init__(self, module_path:Path, spider_name:str):
        self.logger = logging.getLogger(spider_name.lower())
        self.logger_traceback = logging.getLogger(f"{spider_name.lower()}_traceback")
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        module_handler = logging.FileHandler(module_path / Path(f"{spider_name.lower()}.log"))
        module_handler.setLevel(logging.DEBUG)
        module_handler.setFormatter(log_formatter)
        traceback_handler = logging.FileHandler(module_path / Path(f"{spider_name.lower()}_traceback.log"))
        traceback_handler.setLevel(logging.DEBUG)
        traceback_handler.setFormatter(log_formatter)
        self.logger.addHandler(module_handler)
        self.logger_traceback.addHandler(traceback_handler)


class SpiderError:
    SpiderHttpError = SpiderHttpError
    ElementNotFound = ElementNotFound
    SpiderSoupError = SpiderSoupError
    WebScrapingError = WebScrapingError
    ClientPayloadError = ClientPayloadError

    def __init__(self, spider:"Spider"):
        self.spider = spider


    def raise_http_error(self, msg:str=None, url:str=None, ignore_error:bool=False):
        """Logs and raises an HTTP error. Will only log the error if ignore_error is True."""
        if not msg:
            msg = f"SpiderHttpError: '{self.spider.spider_asset.spider_name}', URL: '{url}'"
        logger.error(msg)
        if not ignore_error:
            raise self.SpiderHttpError(msg)


class AiohttpSpider():
    """Asynchronous functionality for the base Spider class with aiohttp package"""

    def __init__(self, spider:Spider):
        self.spider = spider
        self.session = aiohttp.ClientSession()


    async def test_scrape(self, url:str, outfile_name:str=None):
        """Scrape the page and save the resulting HTML to a file.
        This method is to help troubleshoot problems when we aren't
        receiving the HTML from the server that we expect.
        
        *NOTE This method makes an HTTP Request
        """
        logger.info(f'Sending request to {url}')
        res = await self.get(url)
        logger.info(f'Response status: {res.status}')
        if res.status == 200:
            soup = self.spider.get_soup(await res.text())
            if not outfile_name:
                outfile_name = "aio_test_scrape.html"
            else:
                if outfile_name[-5:] != ".html":
                    outfile_name = f"{outfile_name}.html"
            with open(outfile_name, 'w') as f:
                f.write(soup.prettify())
            logger.info(f'Saved response to {os.getcwd()}/{outfile_name}')
        else:
            logger.info('Did not save file due to non 200 status code')


    async def scrape_image(self, image_element:"SpiderTag", use_proxy:bool=True, src_attribute:str='src', raise_exc:bool=True) -> bytes | None:
        """Scrape the binary data tha represents the product image
        
        *NOTE This method makes an HTTP request.
        """
        image_src_url = self.spider.clean_url(image_element.get(src_attribute), raise_exc)
        if image_src_url:
            response = await self.get(image_src_url, use_proxy=use_proxy)
            if response.status == 200:
                return await response.read()


    async def scrape_image_url(self, url:str, use_proxy:bool=True, raise_exc:bool=True) -> bytes | None:
        """Scrape the binary data tha represents the product image
        
        *NOTE This method makes an HTTP request.
        """
        url = self.spider.clean_url(url, raise_exc)
        response = await self.get(url, use_proxy=use_proxy)
        if response.status == 200:
            image_chunks = []
            async for chunk in response.content.iter_chunked(1024):  # Adjust chunk size as needed
                image_chunks.append(chunk)
            image = b''.join(image_chunks)
            return image
            # return await response.read()


    async def get_or_error(self, url:str, use_proxy:bool=True, **kwargs) -> aiohttp.ClientResponse:
        res = await self.get(url, use_proxy=use_proxy, **kwargs)
        if res.status != 200:
            raise self.spider.errors.SpiderHttpError(f"{url}, use_proxy={use_proxy}")
        return res


    async def get(self, url:str, use_proxy:bool=True, **kwargs) -> aiohttp.ClientResponse:
        """Sends an HTTP request using aiohttp's session.get() method.
        The difference is this function will automatically use the proxy and
        will also automatically randomize the headers (well, the UA of the headers).
        """
        if use_proxy:
            proxy_retry_base_time = 2
            max_wait_time = 60
            # max_wait_time = 3
            retry_count = 0
            while True:
                try:
                    proxy = await self.spider.get_proxy(stateful=False)
                    res = await self.session.get(
                        url=url,
                        proxy = proxy.full_endpoint,
                        headers = self.spider.random_headers(),
                        **kwargs
                    )
                except aiohttp.ClientConnectionError as error:
                    msg = f"{error.__class__.__name__}: '{self.spider.spider_asset.spider_name}' URL: '{url}'  RETRYING..."
                    self.spider.log(
                        e = error,
                        level = LogLevel.WARNING,
                        msg = msg
                    )
                    retry_count += 1
                    exponential_backoff = proxy_retry_base_time * (2 ** retry_count)
                    if exponential_backoff > max_wait_time:
                        self.spider.log(e=error)
                        raise error
                    else:
                        logger.info(msg)
                        logger.info(f"Retrying in {exponential_backoff} seconds...")
                        await asyncio.sleep(exponential_backoff) 
                    continue

                except (ClientHttpProxyError, ClientPayloadError, ConnectionResetError) as error:
                    self.spider.log(
                        e = error,
                        level = LogLevel.WARNING,
                        msg = f"{error.__class__.__name__} '{self.spider.spider_asset.spider_name}' URL: '{url} Retrying..."
                    )
                    retry_count += 1
                    exponential_backoff = proxy_retry_base_time * (2 ** retry_count)
                    if exponential_backoff > max_wait_time:
                        self.spider.log(e=error)
                        raise error
                    else:
                        time.sleep(exponential_backoff) #synchronous otherwise other connections will keep trying.
                    continue

                else: 
                    break

        else:
            res = await self.session.get(url=url, **kwargs)
        return res


    async def close_session(self):
        await self.session.close()


class Spider:
    """Base class for all webscraping spiders"""
    session = None
    url = None
    is_error = False
    error = None

    def __init__(
                self,
                spider_asset:SpiderAsset,
                middleware_manager_interface:SpiderMiddlewareManagerInterface,
                proxy_manager_interface:SpiderProxyManagerInterface,
                p:Optional[AsyncPlaywright]=None,
                test_env:bool = False,
                ):
        self.ua:str = ua_generator.generate(device="desktop").text
        self.headers:dict = self.create_headers()
        self.spider_asset = spider_asset
        self.spider_id = self.spider_asset.id
        self.errors = SpiderError(self)
        self.regex = SpiderRegex(self)
        self.domain = self.spider_asset.domain
        self.url = self._url()
        self.module_logger = SpiderModuleLog(spider_asset.module_dir_path(), spider_asset.spider_name)
        self.middleware_manager_interface = middleware_manager_interface
        self.proxy_manager_interface = proxy_manager_interface
        self.spider_interface = SpiderInterface(self)
        self.fuzzing = SpiderFuzzer
        self.p = p
        self.aio = AiohttpSpider(self) 
        # self.interface = SpiderInterface(self)
        # self.middleware = MiddlewareManager(self.interface)
        # self.proxy = ProxyManager(self.interface)
        if not test_env:
            self.params = self.get_params()


    @property
    def sentinel(self) -> str:
        """Retursn the sentinel value"""
        return SENTINEL


    def _url(self) -> str:
        if self.domain.startswith("https://"):
            return self.domain
        return f"https://{self.domain}"



    def clean_url(self, url:str|None, raise_exc:bool=False) -> str|None:
        """Sometimes <img> src attributes, or <a> href attributes need to be
        cleaned up a bit before making a new web request.
        """
        url = url.strip().replace(' ', '%20')
        if not url:
            self.log(f"TypeError {self.spider_asset.spider_name}: URL '{url}' passed to Spider.clean_url() is None!")
            return
        if url.startswith('//'):
            url = f"https:{url}"
        elif url.startswith('/'):
            url = f"https://{self.spider_asset.domain}{url}"

        if validators.url(url):
            return url
        else:
            msg = f"({self.spider_asset.spider_name}): URL '{url}' passed to Spider.clean_url() is invalid!"
            if raise_exc:
                raise ValueError(msg)
            else:
                self.log(msg)
                return url


    def random_headers(self) -> dict:
        """Currently headers is static except for UA. 
        Will put in functionality here to make the other 
        headers more dynamic.
        """
        headers = {
            "User-Agent": ua_generator.generate(device="desktop").text,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",  # Do Not Track Request Header
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",   
        }
        return headers


    async def get_proxy(self, stateful:bool=False) -> ProxySession | None:
        """Create a new ProxySession object"""
        try:
            return await self.proxy_manager_interface.create_proxy_session(stateful)
        except AttributeError as e:
            return None

    def get_params(self) -> dict[str, str]:
        """Retrieves the spider's params from the registry."""
        return scraping_registry.registry[self.spider_id].params


    def soup_check(self, soup:SpiderSoup):
        """Bang out HTML file to attack in ipython"""
        with open('soup_check.html', 'w') as f:
            f.write(soup.prettify())


    def get_soup(self, markup:str|bytes, **kwargs) -> SpiderSoup|None:
        """Instantiates the SpiderSoup object.

        Logs error and sets self.is_error to True if SpiderSoup fails
        to instantiate.
        """
        soup = None
        spider_name = self.__class__.__name__
        try:
            soup = SpiderSoup(spider_name=spider_name, markup=markup, features='lxml', **kwargs)
        except BadMarkupError as e:
            self.log(f"{e.__class__.__name__}({e.spider_name}): {e.error_details}")
        return soup


    def spider_state(self) -> SpiderState:
        """NOTE DEPRECATED!! use get_state() instead
        Gets the current state of the spider in the spider registry.
        """
        return scraping_registry.get_spider_state(self.spider_id)


    def get_state(self) -> SpiderState:
        """Gets the current state of the spider in the spider registry."""
        return scraping_registry.get_spider_state(self.spider_id)


    def shuffle(self, list_to_shuffle:list) -> None:
        """Shuffle the order of the list in place"""
        random.shuffle(list_to_shuffle)
        return


    def check_state(self) -> bool:
        """Checks the spider's state and returns False if it is
        any other state besides 'RUNNING'.
        """
        if self.spider_state() == SpiderState.RUNNING:
            return True
        return False


    def create_headers(self) -> dict:
        """Currently headers is static except for UA. 
        Will put in functionality here to make the other 
        headers more dynamic.
        """
        headers = {
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",  # Do Not Track Request Header
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1",   
        }
        return headers


    def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR, msg:str=None):
        """Logging method if individual spiders need to log an error."""
        if not msg:
            msg = f"{repr(e)}"
        match level:
            case LogLevel.EXCEPTION:
                self.module_logger.logger.exception(msg)
            case LogLevel.CRITICAL:
                self.module_logger.logger.critical(msg)
                self.module_logger.logger_traceback.exception(msg)
            case LogLevel.ERROR:
                self.module_logger.logger.error(msg)
                self.module_logger.logger_traceback.exception(msg)
            case LogLevel.WARNING:
                self.module_logger.logger.warning(msg)
            case LogLevel.INFO:
                self.module_logger.logger.info(msg)
            case LogLevel.DEBUG:
                self.module_logger.logger.debug(msg)
            case _:
                self.module_logger.logger.critical(f"Unexpected log level: {level}. Original error: {msg}")
                self.module_logger.logger_traceback.exception(f"{msg}")
        return


    # def raise_error(self, e:WebScrapingError, as_e:BaseException):
    #     """Logs error and then sets self.is_error to True and sets self.error
    #     to the class name of the error "e".
    #     """
    #     logger.error(f"{repr(e)}: {as_e}")
    #     self.is_error = True
    #     self.error = e
    #     return


    async def jitter(self, low:float=0, high:float=2):
        """A randomized delay that can be made between requests"""
        await asyncio.sleep(random.uniform(low, high))
        return


    async def random_delay(self, low:int=1, high:int=5):
        """**DEPRECATED**
        use self.jitter() instead

        Random time delay. 
        To make us look more human :)
        """
        s = random.randint(low, high)
        await asyncio.sleep(s)
        return







class PlaywrightSpider(Spider):
    """This class adds playwright functionality to our spider class."""
    
    def __init__(self, spider_asset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.p:AsyncPlaywright = kwargs.get('p', None)
        self.browser:Browser = None


    async def start(self, browser:str='chromium', headless:bool=True):
        """Launch async webdriver and get a blank page."""
        match browser:
            case 'firefox':
                self.browser = await self.p.firefox.launch(headless=headless)
            case 'webkit':  # requires more libraries
                self.browser = await self.p.webkit.launch(headless=headless)
            case _:
                self.browser = await self.p.chromium.launch(headless=headless)
        return
    
    

    async def _new_browser_context(self, proxy:ProxySession=None) -> BrowserContext:
        """Create a new Playwright BrowserContext, either with proxy config details
        or without proxy entirely.
        """
        if proxy:
            browser_context = await self.browser.new_context(proxy={
                'server': proxy.endpoint,
                'username': os.getenv("PROXY_USER"),
                'password': os.getenv("PROXY_PASS"),
            })
        else:
            browser_context = await self.browser.new_context()
        return browser_context


    async def new_context(self, stateful:bool=False, proxy:bool=True) -> SpiderContext:
        """Factory method for creating new SpiderContext objects:
            -creates RequestContext if request is stateful,
            -creates ProxySession object if request is proxied, 
            -creates the underlying Playwright BrowserContext object,
        then passes it all into SpiderContext along with its self.
        """
        if PROXY and proxy:
            if stateful:
                proxy = await self.get_proxy(stateful=True)
                request_context = RequestContext()
            else:
                proxy = await self.get_proxy()
                request_context = None
        else:
            proxy = None
            request_context = RequestContext()
        browser_context = await self._new_browser_context(proxy=proxy)
        return SpiderContext.create(
            self, 
            context=browser_context, 
            request_context=request_context,
            proxy=proxy, 
        )


    async def new_page(self, spider_context:SpiderContext=None) -> SpiderPage:
        """Factory method which calls SpiderPage's factory method for creating a 
        new SpiderPage. This enables us to create new SpiderPage objects without
        having to import SpiderPage on every new webscraping module we make.
        """
        if spider_context:
            new_page = await spider_context.context.new_page()
        else:
            new_page = await self.browser.new_page()
        return await SpiderPage.create(self, new_page, spider_context)











# class RequestsSpider(Spider):
#     """This class gives python's requests library functionality to
#     our spiders.
#     """
#     def get(self, session:requests.Session, **kwargs) -> requests.Response | None:
#         """Wrapper function for requests library's session.get() with
#         included error handling.

#         *If the request fails this method will return None. Always check 
#         to make sure the return value is a Response object and not None.
#         """
#         res = None
#         try:
#             res = session.get(self.url, timeout=5, **kwargs)
#         except (requests.RequestException, requests.Timeout) as e:
#             self.log(SpiderHttpError(repr(e)), LogLevel.ERROR)

#         return res


#     def session(self, **kwargs) -> requests.Session:
#         """Initialize the requests.Session object, along with 
#         any attributes of our choosing.
#         """
#         s = requests.Session()
#         s.headers = self._headers()
#         for key, value in kwargs.items():
#             setattr(s, key, value)
#         return s


