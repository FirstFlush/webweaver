
from typing import TYPE_CHECKING, Any
from playwright.async_api import Response as ResponsePlaywright
from aiohttp import ClientResponse as ResponseAiohttp

from webweaver.common.utils import import_class_from_string
from webweaver.config import REQUEST_MIDDLEWARES, RESPONSE_MIDDLEWARES
from webweaver.exceptions import ResponseUnsupported, WebScrapingError
from webweaver.common.enums import LogLevel
from webweaver.webscraping.middleware.generic_response import GenericResponse

if TYPE_CHECKING:
    from webweaver.webscraping.spiders.spider_base import SpiderInterface
    from webweaver.webscraping.spiders.spider_page import RequestContextInterface
    from webweaver.webscraping.middleware.middleware_base import MiddlewareBase


class SpiderMiddlewareManagerInterface:
    """Interface for the spider to pass a Response through to 
    the middleware manager for middleware processing.
    """
    def __init__(self, manager:"MiddlewareManager"):
        self.manager = manager

    async def handle_response(self, 
                              response:Any, 
                              spider_interface:"SpiderInterface",
                              request_interface:"RequestContextInterface"=None
                              ):
        """The spider passes its logging interface to the middleware manager, along with
        the response. This method will create a GenericResponse object, and then
        run the various response middleware modules against it. 
        This design allows middleware modules to write to spider's module-level logs
            *Currently only have 1 lonely StatusCode middleware module
        """
        if request_interface:
            generic_response = self.manager.create_generic_response(response, spider_interface)
            await self.manager.run_response_middlewares(
                generic_response=generic_response,
                spider_interface=spider_interface,
                request_interface=request_interface
            )


# class MiddlewareManagerInterface:

#     def __init__(self, manager:"MiddlewareManager"):
#         self.manager = manager


    # def log(self, e:WebScrapingError=None, level:LogLevel=LogLevel.ERROR):
    #     self.manager.spider_interface.log(e, level)


class MiddlewareManager:

    def __init__(self):
        # self.spider_interface = spider_interface
        self.request_middlewares:list[MiddlewareBase] = [import_class_from_string(path) for path in REQUEST_MIDDLEWARES]
        self.response_middlewares:list[MiddlewareBase] = [import_class_from_string(path) for path in RESPONSE_MIDDLEWARES]
        self.spider_middleware_manager_interface = SpiderMiddlewareManagerInterface(self)
        # self.middleware_manager_interface = MiddlewareManagerInterface(self)


    async def run_response_middlewares(
            self, 
            generic_response:GenericResponse, 
            spider_interface:"SpiderInterface",
            request_interface:"RequestContextInterface"
        ):
        """This method runs the response middlewares"""
        if not isinstance(generic_response, GenericResponse):
            raise ResponseUnsupported(repr(generic_response))
        for middleware_class in self.response_middlewares:
            middleware = middleware_class(
                spider_interface = spider_interface,
                request_interface = request_interface,
                response = generic_response
            )
            await middleware.handle_response()


    def create_generic_response(self, response:Any, spider_interface:"SpiderInterface") -> GenericResponse:
        """Takes the response object and converts it into a GenericResponse object, 
        so that our middleware can process it in a consistent manner.
        """
        if isinstance(response, ResponsePlaywright):
            generic_response = GenericResponse.from_playwright(response)
        elif isinstance(response, ResponseAiohttp):
            generic_response = GenericResponse.from_aiohttp(response)
        else:
            spider_interface.log(ResponseUnsupported(
                f"{type(response)} Unsupported! MiddlewareManager can not generate GenericResponse")
            )
            raise ResponseUnsupported
        return generic_response