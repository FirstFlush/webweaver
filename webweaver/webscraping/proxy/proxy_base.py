from datetime import datetime
import os
import random
from typing import TYPE_CHECKING, Optional
# from exceptions import SpiderRetryTimeout
# from webscraping.proxy.proxy_endpoints import ProxyEndpoints
# from webscraping.proxy.request_handler import ProxyRequestHandler

if TYPE_CHECKING:
    from webweaver.webscraping.proxy.proxy_manager import SessionProxyManagerInterface


# class RequestContext:
#     """The shared-state between multiple requests within the
#     same ProxySession. This class being present in ProxySession's
#     instantiation makes the ProxySession stateful.
#     """
#     def __init__(self):
#         # self.port = port  # the proxy endpoint port
#         self.retry_count = 0
#         self.base_wait_time = 30  # 30 seconds
#         self.max_wait_time = 3600  # 1 hour
#         self.begin = datetime.utcnow()

#     def calculate_wait_time(self) -> int:
#         """Retrieve the wait time with the exponential backoff algorithm, and then
#         increase the retry count by 1.
#         """
#         wait_time = self.exponential_backoff()
#         self.retry_count += 1
#         return wait_time

#     def exponential_backoff(self) -> int:
#         """Calculates the time (in seconds) this spider/proxy should wait 
#         before retrying using an exponential backoff algorithm.
#         Raises a SpiderRetryTimeout if the time required to wait is greater 
#         than our max.
#         """
#         wait_time = min(self.base_wait_time * (2 ** self.retry_count), self.max_wait_time)
#         if wait_time == self.max_wait_time:
#             raise SpiderRetryTimeout
#         return wait_time


class ProxySession:
    """This class governs the communication with the proxy service endpoint.
    If we have 100 IPs to scrape with then 100 ProxySessions will be made. This
    approach allows some proxy sessions to be stateless and some to be stateful.
    Stateful ProxySession objects have a RequestContext object to manage state between
    requests.

    ProxySessions can also share state via the methods in their self.manager_interface
    class, which is an interface for getting/setting state in the ProxyManager object
    that created them all.
    """
    def __init__(
            self, 
            endpoint:str,
            manager_interface:"SessionProxyManagerInterface", 
            # request_context:Optional[RequestContext],
            ):
        self.endpoint = endpoint
        self.manager_interface = manager_interface
        # self.request_context = request_context


    @property
    def full_endpoint(self) -> str:
        """Includes the username/pass in the proxy endpoint"""
        return f"http://{os.getenv('PROXY_USER')}:{os.getenv('PROXY_PASS')}@{self.endpoint.replace('http://','')}"


    async def release(self):
        """Releases the proxy endpoint so that other proxysession objects
        may use it.
        """
        await self.manager_interface.release_endpoint(self.endpoint)
        return


    def jitter(self) -> int:
        return random.randint(0, 10)


    
    # def url_cache_callback(self, response):
    #     """Callback passed to ProxySession so ProxyManager"""
    #     url:str = response.url
    #     if url not in self.scraped_urls:
    #         self.scraped_urls.add(url)
    #         ...



