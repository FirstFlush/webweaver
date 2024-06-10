from functools import wraps
from typing import Callable
from playwright.async_api import Response as ResponsePlaywright
from aiohttp import ClientResponse as ResponseAiohttp

"""
Decorator(s) to process middleware modules when making 
a request or receiving a response.
"""

def response_middleware(func:Callable):
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> ResponsePlaywright|ResponseAiohttp|None:
        # Call the original function and get the response
        response = await func(self, *args, **kwargs)
        if response is None:
            return response
        # Extract the relevant arguments
        request_interface = kwargs.get('request_interface')
        # request_interface = self.spider_context.request_interface if request_interface else None

        # Perform the desired operation with the extracted arguments
        await self.spider_interface.call_middleware(
            response=response, 
            request_interface=request_interface
        )

        # Return the response from the original function
        return response

    return wrapper













# def response_middleware(func:Callable):
#     @wraps(func)
#     async def wrapper(self, *args, **kwargs) -> ResponsePlaywright|ResponseAiohttp|None:
#         # Call the original function and get the response
#         response = await func(self, *args, **kwargs)
#         if response is None:
#             return response
#         # Extract the relevant arguments
#         spider_interface = self.spider.spider_interface
#         request_interface = kwargs.get('request_interface')
#         # request_interface = self.spider_context.request_interface if request_interface else None

#         # Perform the desired operation with the extracted arguments
#         await self.spider.middleware_manager_interface.handle_response(
#             response=response, 
#             spider_interface=spider_interface,
#             request_interface=request_interface
#         )

#         # Return the response from the original function
#         return response

#     return wrapper