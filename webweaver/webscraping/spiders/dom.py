from asyncio import sleep as async_sleep
import json
import logging
import math
import random
from typing import TYPE_CHECKING
from playwright.async_api import Page, ElementHandle
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError, 
    Error as PlaywrightError, 
    Response as ResponsePlaywright
)
from webweaver.exceptions import SpiderHttpError, ClickLinkError
from webweaver.common.constants import VIEWPORTS, PLUGINS
from webweaver.webscraping.middleware.decorators import response_middleware

if TYPE_CHECKING:
    from webweaver.webscraping.spiders.spider_base import SpiderInterface

logger = logging.getLogger('scraping')


class PageCursor:

    def __init__(self, page:Page):
        self.page = page

    def generate_curved_path(self, start_x, start_y, end_x, end_y, steps=20):
        """Generates a curve based on a sin wave."""
        path = []
        for i in range(steps):
            t = i / (steps - 1)
            x = (1 - t) * start_x + t * end_x
            y = (1 - t) * start_y + t * end_y + math.sin(t * math.pi) * 50  # Sin wave for curve
            # Adding randomness
            x += random.uniform(-5, 5)
            y += random.uniform(-5, 5)
            path.append((x, y))
        return path

    async def human_like_mouse_move(
        self, 
        start_x:int, 
        start_y:int, 
        end_x:int, 
        end_y:int,
        steps:int=20
    ):
        """Moves the mouse cursor in a sin-wave pattern to make the 
        webscraper appear more human-like.
        """
        path = self.generate_curved_path(start_x, start_y, end_x, end_y, steps)
        for x, y in path:
            await self.page.mouse.move(x, y)
            await async_sleep(random.uniform(0.05, 0.15))


    async def test_human_like_mouse_move(
        self, 
        start_x:int, 
        start_y:int, 
        end_x:int, 
        end_y:int
    ):
        """Moves the mouse cursor in a sin-wave pattern to appear more humanlike.

        *This function is for testing purposes! There is JS here to track the cursor
        movements and print them to the terminal.
        """
        await self.page.evaluate('''() => {
            window.mousePositions = [];
            document.addEventListener('mousemove', event => {
                window.mousePositions.push({x: event.clientX, y: event.clientY});
            });
        }''')

        path = self.generate_curved_path(start_x, start_y, end_x, end_y)
        for x, y in path:
            await self.page.mouse.move(x, y)
            await async_sleep(random.uniform(0.05, 0.15))
            position = await self.page.evaluate('window.mousePositions[window.mousePositions.length - 1]')
            print(f"Mouse moved to: {position}")


class PageScroll:

    def __init__(self, page:Page):
        self.page = page

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


    async def scroll_into_view(self, element:ElementHandle, timeout:float=3000):
        """Scrolls the element into view. Used to appear more human when clicking on links.
            -Might be adding more functionality to this, like some small jitter time.
        """
        element.scroll_into_view_if_needed(timeout)
        return




class PageConfig:

    def __init__(self, page:Page):
        self.page = page

    async def get_config(self):
        """Get all DOM configuration variables that could 
        potentially be used to detect webscraping.

        #TODO How to fake the pluginArray?

        """
        webdriver               = await self.page.evaluate('navigator.webdriver')
        platform                = await self.page.evaluate('navigator.platform')
        language                = await self.page.evaluate('navigator.language')
        languages               = await self.page.evaluate('navigator.languages')
        user_agent              = await self.page.evaluate('navigator.userAgent')
        plugins                 = await self.page.evaluate('navigator.plugins')
        hardware_concurrency    = await self.page.evaluate('navigator.hardwareConcurrency')
        screen_width            = await self.page.evaluate('window.screen.width')
        screen_height           = await self.page.evaluate('window.screen.height')
        avail_screen_width      = await self.page.evaluate('window.screen.availWidth')
        avail_screen_height     = await self.page.evaluate('window.screen.availHeight')
        color_depth             = await self.page.evaluate('window.screen.colorDepth')
        window_outer_width      = await self.page.evaluate('window.outerWidth')
        window_outer_height     = await self.page.evaluate('window.outerHeight')
        pixel_ratio             = await self.page.evaluate('window.devicePixelRatio')
        document_hidden         = await self.page.evaluate('document.hidden')
        window_history_length   = await self.page.evaluate('window.history.length')
        has_focus               = await self.page.evaluate('document.hasFocus()')
        # web_gl_rendering_context = await self.page.evaluate('window.WebGLRenderingContext')
        chrome = await self.page.evaluate('window.chrome')

        logger.debug(f'navigator.webdriver:             {webdriver}')
        logger.debug(f'navigator.platform:              {platform}')
        logger.debug(f'navigator.language:              {language}')
        logger.debug(f'navigator.languages:             {languages}')
        logger.debug(f'navigator.userAgent:             {user_agent}')
        logger.debug(f'navigator.plugins:               {plugins}')
        logger.debug(f'navigator.hardwareConcurrency:   {hardware_concurrency}')
        logger.debug(f'window.screen.width:             {screen_width}')
        logger.debug(f'window.screen.height:            {screen_height}')
        logger.debug(f'window.screen.availWidth:        {avail_screen_width}')
        logger.debug(f'window.screen.availHeight:       {avail_screen_height}')
        logger.debug(f'window.screen.colorDepth:        {color_depth}')
        logger.debug(f'window.outerWidth:               {window_outer_width}')
        logger.debug(f'window.outerHeight:              {window_outer_height}')
        logger.debug(f'window.devicePixelRatio:         {pixel_ratio}')
        logger.debug(f'document.hidden:                 {document_hidden}')
        logger.debug(f'window.history.length:           {window_history_length}')
        logger.debug(f'document.hasFocus():             {has_focus}')
        logger.debug(f'window.chrome:                   {chrome}')
        # print('window.WebGLRenderingContext: ', web_gl_rendering_context)



    async def set_page_config(self):
        """Set various config settings for a new SpiderPage object."""
        await self._set_viewport()
        await self._hide_webdriver()
        await self._set_window_history_length()
        await self._set_languages()
        await self._set_platform()

        # print("\n\n")
        # print(await self.page.evaluate("navigator.plugins"))
        # print("\n\n")

        return
    

    async def _set_platform(self):
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'platform', {
               get: () => 'Win32'                      
            });
        """)


    async def _set_window_history_length(self):
        """Sets the window.history.length property to something greater than 1"""
        await self.page.add_init_script("""
            Object.defineProperty(window.history, 'length', {
                get: () => Math.floor(Math.random() * 10) + 3
            });
        """)


    async def _get_plugins(self) -> str:
        """Returns a serialized string of the browser's actual plugin values.
        Running page.evaluate("navigator.plugins") returns a mostly-empty object.
        """
        plugins_json = await self.page.evaluate("""
            JSON.stringify(Object.fromEntries(Array.from(navigator.plugins).map(
                p => [p.name, {
                    name: p.name,
                    filename: p.filename,
                    description: p.description,
                    mimeTypeCount: p.length,
                    mimeTypes: Object.fromEntries(Array.from(p).map(
                        m => [m.type, { type: m.type, suffixes: m.suffixes, description: m.description }]
                    ))
                }]
            )));
        """)

        return plugins_json


    async def _set_plugins(self):
        """Sets the navigator.plugins value. Now in headless mode plugins
        will actually show up.
        """
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => (""" + f"{PLUGINS}" + """)
            });"""
        )

    async def _set_viewport(self):
        """Sets the page's viewport to that of a standard desktop computer."""
        viewport = random.choice(VIEWPORTS)
        await self.page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
        return


    async def _set_languages(self):
        """Sets the navigator.language and navigator.languages values"""
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
               get: () => [ "en-US", "en" ]                         
            });
            Object.defineProperty(navigator, 'language', {
               get: () => "en-US"                         
            });
        """)

    async def _hide_webdriver(self):
        """Sets the 'navigator.webdriver' property from true to false"""
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false 
            });
        """)


class PageNavigation:

    def __init__(self, spider_interface:"SpiderInterface", page:Page):
        self.spider_interface = spider_interface
        self.page = page

    # TODO these functions will need to be altered since its being pulled out of SpiderPage class
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


    @response_middleware
    async def goto_or_none(self, url, timeout:float=100000, **kwargs) -> ResponsePlaywright|None:
        """Calls self.goto_or_error() and returns None if an error is raised."""
        try:
            return await self.goto_or_error(url, timeout, **kwargs)
        except SpiderHttpError as e:
            self.spider_interface.log(e)
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
