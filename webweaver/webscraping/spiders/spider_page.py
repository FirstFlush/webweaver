from asyncio import sleep as async_sleep
# from datetime import datetime, timedelta
import logging
import random
from typing import TYPE_CHECKING

from playwright._impl._api_types import (
    TimeoutError as PlaywrightTimeoutError, 
    Error as PlaywrightError
)
from playwright.async_api import (
    Page, 
    BrowserContext,
    ElementHandle, 
    Response as ResponsePlaywright
)
from webweaver.common.utils import VIEWPORTS
from webweaver.exceptions import SpiderHttpError, ClickLinkError
from webweaver.webscraping.spiders.dom import (
    PageConfig,
    PageCursor,
    PageNavigation,
    PageScroll
)
if TYPE_CHECKING:
    from webweaver.webscraping.proxy.proxy_base import ProxySession
    from webweaver.webscraping.spiders.spider_base import Spider


from webweaver.webscraping.middleware.decorators import response_middleware


logger = logging.getLogger('scraping')


class RequestContextInterface:

    def __init__(self, request_context:"RequestContext"):
        self.request_context = request_context

    def increase_retry_count(self):
        self.request_context.retry_count += 1
        return

    @property
    def retry_count(self) -> int:
        return self.request_context.retry_count


class RequestContext:
    """The shared-state between multiple requests within the
    same SpiderContext. 
    This is also the object Middleware will operate on.
    """
    def __init__(self):
        self.retry_count = 0
        # self.begin = datetime.utcnow()
        self.url = None



class SpiderContext():
    """Wrapper class to extend the functionality of Playwright's BrowserContext object.
    When using a proxy in Playwright, the proxy is passed into the BrowserContext object
    upon instantiation. The SpiderContext object will keep the ProxySession object for
    as long as the session is needed.
    """
    def __init__(
            self, 
            spider: "Spider",
            context:BrowserContext,
            request_context:RequestContext=None,
            proxy:"ProxySession"=None,
            ):
        logger.debug(f"init proxy: {proxy}")
        logger.debug(f"init request_context: {request_context}")

        self.spider = spider
        self.context = context
        self.proxy = proxy
        self.request_context = request_context
        if self.request_context:
            self.request_interface = RequestContextInterface(request_context)
        else:
            self.request_interface = None

    @property
    def is_stateful(self) -> bool:
        return self.request_context is not None

    async def new_spider_page(self) -> "SpiderPage":
        """Create a new SpiderPage object, controlled by this SpiderContext."""
        page = await self.context.new_page()
        return await SpiderPage.create(
            spider = self.spider, 
            page = page, 
            spider_context = self
        )


    @staticmethod
    def create(
            spider:"Spider", 
            context:BrowserContext, 
            request_context:RequestContext=None,
            proxy:"ProxySession"=None, 
        ) -> "SpiderContext":
        """Factory method for creating new SpiderContext objects."""
        spider_context = SpiderContext(
            spider=spider, 
            context=context, 
            request_context=request_context,
            proxy=proxy
        )
        return spider_context





class SpiderPage():
    """Wrapper class to extend the functionality of Playwright's Page object."""
    def __init__(self, spider:"Spider", page:Page, spider_context:SpiderContext):
        self.spider = spider
        self.page = page
        self.spider_context = spider_context

        self.config = PageConfig(self.page)
        self.cursor = PageCursor(self.page)
        self.navigation = PageNavigation(self.spider.spider_interface, self.page)
        self.scroll = PageScroll(self.page)


    @staticmethod
    async def create(spider:"Spider", page:Page, spider_context:SpiderContext) ->"SpiderPage":
        """Factory method for creating new SpiderPage objects 
        while avoiding having to make the init function async
        """
        spider_page = SpiderPage(spider, page, spider_context)
        await spider_page.config.set_page_config()
        return spider_page


    # async def jitter(self, low:float=0, high:float=2):
    #     """A randomized delay that can be made between requests"""
    #     await async_sleep(random.uniform(low, high))



    async def check_element(self, element:ElementHandle, timeout:float=100000, **kwargs) -> ElementHandle|None:
        """Check if an element exists. If it does, return the element. 
        Otherwise, return None.
        """
        try:
            return await self.page.wait_for_selector(selector=element, timeout=timeout, **kwargs)
        except PlaywrightTimeoutError:
            return None


    async def set_page_config(self):
        """Set various config settings for a new SpiderPage object."""
        await self._set_viewport()
        await self._hide_webdriver()
        return


    async def _set_viewport(self):
        """Sets the page's viewport to that of a standard desktop computer."""
        viewport = random.choice(VIEWPORTS)
        await self.page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
        return


    async def _hide_webdriver(self):
        """Sets the 'navigator.webdriver' property from true to false"""
        await self.page.add_init_script("""
            navigator.webdriver = undefined;
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false 
            })
        """)


    async def _get_scroll_values(self, element_selector:str) -> dict:
        """Returns the values of the web browser's scrollTop & scrollHeight
        DOM properties. used in the self.infinite_scroll() method.
        """
        values = await self.page.evaluate(f"""
            const container = document.querySelector('{element_selector}');
            ({{
                scrollTop: container.scrollTop,
                scrollHeight: container.scrollHeight
            }});
        """)
        return values


    async def infinite_scroll(self, element_selector:str, timeout:int=3000):
        """Keep scrolling until we reach the bottom using Javascript:

        container.scrollHeight  -Check the height of the container
        container.scrollTop     -Set this to scrollHeight value to scroll to bottom
        """
        previous_scrollTop = None
        while True:
            await self.page.evaluate(f"""
            const container = document.querySelector('{element_selector}');
            container.scrollTop = container.scrollHeight;
            """)
            await self.page.wait_for_timeout(timeout)
            values = await self._get_scroll_values(element_selector)
            if values['scrollTop'] == previous_scrollTop:
                break
            previous_scrollTop = values['scrollTop']

        return

    async def infinite_scroll2(self, element_selector:str, timeout:int=3000):
        """on GreenSociety spider the regular infinite_scroll did not work.
            *Use this method ONLY if the entire body grows as new records are added.
        """
        scroll_height_previous = 0
        while True:
            scroll_height = await self.page.evaluate(f"""
            const el = document.querySelector('{element_selector}');
            el.scrollIntoView();
            document.body.scrollHeight;
            """)
            await self.page.wait_for_timeout(timeout)
            if scroll_height == scroll_height_previous:
                break
            scroll_height_previous = scroll_height
        return

    # async def close_modal(self, close_modal_selector:str):
        



    async def scroll_into_view(self, element:ElementHandle, timeout:float=3000):
        """Scrolls the element into view. Used to appear more human when clicking on links.
            -Might be adding more functionality to this, like some small jitter time.
        """
        element.scroll_into_view_if_needed(timeout)
        return


    async def click_link(self, element:ElementHandle, max_retries:int=5, verbose:bool=True):
        retries = 0
        while retries < max_retries:
            try:
                async with self.page.expect_navigation() as navigation_info:
                    await  element.click()
                response = await navigation_info.value
                if verbose:
                    print(f">> {response.url}")
                    print(f">> {response.status}")
                return
            except (AttributeError, PlaywrightTimeoutError):
                retries += 1
                if verbose:
                    print(f">> Click link failed. Retrying x{retries}...")
                await async_sleep(2)
                continue
        raise ClickLinkError(await element.inner_html())


    # @response_middleware
    async def goto_or_none(self, url, timeout:float=100000, **kwargs) -> ResponsePlaywright|None:
        """Calls self.goto_or_error() and returns None if an error is raised."""
        try:
            return await self.goto_or_error(url, timeout, **kwargs)
            # response = await self.goto_or_error(url, timeout, **kwargs)
            # await self.spider.middleware_manager_interface.handle_response(
            #     response=response, 
            #     spider_interface=self.spider.spider_interface,
            #     request_interface=self.spider_context.request_interface
            # )
            # return response
        
        except SpiderHttpError as e:
            self.spider.log(e)
            return None


    async def goto_or_error(self, url, timeout:float=100000, **kwargs) -> ResponsePlaywright:
        """Wrapper function for playwright's page.goto() method to
        includes error handling and logging.

        *timeout is in milliseconds.
        *Ensure this method returns a ResponsePlaywright object, and not None!
        """
        try:
            return await self.page.goto(url, timeout=timeout, **kwargs)
        except (PlaywrightError, PlaywrightTimeoutError) as e:
            logger.error(SpiderHttpError(f"{repr(e)}"))
            raise SpiderHttpError(repr(e))
