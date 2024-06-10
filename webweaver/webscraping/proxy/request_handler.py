# from typing import Any
# from types import MethodType
# from playwright.async_api import ElementHandle

# from exceptions import ProxyRequestError, SpiderRetryTimeout
# from webscraping.spiders.spider_page import SpiderPage
# # from middleware.middleware_manager import SpiderMiddlewareManager

# class ProxyRequestHandler:
#     """This class allows a ProxySession to make a request to the proxy service

#     """
#     async def click(self, spider_page:SpiderPage, element:ElementHandle, *args, **kwargs) -> SpiderPage:
#         """Wrapper for playwright's click() method
#         # This function seems like its best avoided lol. grab the URL and call spider_page.goto() instead of clicking
#         """
#         click_response = await spider_page.click_link(element, *args, **kwargs)
#         await spider_page.page.wait_for_load_state('networkidle')
#         return spider_page


#     async def request(self, request_func:MethodType, *args, **kwargs) -> Any:
#         print(type(request_func))
#         try:
#             response = await request_func(*args, **kwargs)
#         except Exception as e:
#             raise ProxyRequestError(e)

#         return response