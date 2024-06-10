# from typing import TYPE_CHECKING, Any
# from exceptions import SpiderRequestError, SpiderRetryTimeout

# if TYPE_CHECKING:
#     from webscraping.spiders.spider_base import Spider



# class RequestLauncher:
#     """Each Proxy object will have its own RequestLauncher & RetryContext/RequestContext
#     This clas provides a unified way of sending requests and managing requests state.
#     """
#     def __init__(self, spider:Spider):
#         self.spider = spider

#     async def request(self, request_func:function, *args, **kwargs) -> Any|None:
#         print(type(request_func))
#         try:
#             response = await request_func(*args, **kwargs)
#         except Exception as e:
#             self.spider.log(SpiderRequestError(e))
#             response = None
#         return response