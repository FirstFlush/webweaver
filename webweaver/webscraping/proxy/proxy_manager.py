
import asyncio 
import logging
import os

from webweaver.config import PROXY
from webweaver.webscraping.proxy.proxy_base import (
    # RequestContext, 
    ProxySession 
)
from webweaver.webscraping.proxy.proxy_endpoints import ProxyEndpoints


logger = logging.getLogger('scraping')


class SpiderProxyManagerInterface:
    """Interface to be passed to spiders so that spider can interact with
    proxy manager in a consistent way
    """
    def __init__(self, proxy_manager:"ProxyManager"):
        self.proxy_manager = proxy_manager


    async def create_proxy_session(self, stateful:bool=False) -> ProxySession:
        """spider creates a ProxySession object. 
        gets an endpoint assigned if its sticky
        """
        return await self.proxy_manager.create_proxy_session(stateful)



class SessionProxyManagerInterface:
    """Interface to be passed into ProxySession objects so that they can interact
    with ProxyManager. ProxyManager acts as a shared state for ProxySession instances 
    via ProxyManagerInterface
    """
    def __init__(self, manager:"ProxyManager"):
        self.manager = manager


    async def release_endpoint(self, endpoint:str):
        await self.manager.release_sticky_endpoint(endpoint)


    # def is_url_scraped(self, url:str) -> bool:
    #     return url in self.manager.scraped_urls

    # async def cache_url(self, url:str):
    #     async with self.manager.lock:
    #         self.manager.scraped_urls.add(url)




class ProxyManager:
    """This is the shared-state between all instances of ProxySession."""
    def __init__(self):
        PROXY_USER = os.environ.get('PROXY_USER')
        PROXY_PASS = os.environ.get('PROXY_PASS')
        self.endpoint_lock = asyncio.Lock()
        self.endpoint_condition = asyncio.Condition(self.endpoint_lock)
        self.spider_manager_interface = self._create_spider_interface()
        self.session_manager_interface = self._create_session_interface()
        self.endpoints = ProxyEndpoints(PROXY_USER, PROXY_PASS)


    def _create_session_interface(self) -> SessionProxyManagerInterface:
        """Creates an interface object to be passed into each new ProxySession
        object so ProxySession can communicate with ProxyManager via a consistent API.
        """
        return SessionProxyManagerInterface(self)

    def _create_spider_interface(self) -> SpiderProxyManagerInterface|None:
        """Return the Spider's proxy maanger interface if PROXY=True 
        in config settings. Otherwise return None.
        """
        return SpiderProxyManagerInterface(proxy_manager=self) if PROXY else None


    async def get_sticky_endpoint(self) -> str:
        """Retrieve a sticky endpoint. If all endpoints are in use (in the self.endpoints.in_use set)
        then this function will perform an async wait() until the resource has been freed.
        """
        async with self.endpoint_condition:
            while True:
                for endpoint in self.endpoints.sticky:
                    if endpoint not in self.endpoints.in_use:
                        self.endpoints.in_use.add(endpoint)
                        return endpoint
                await self.endpoint_condition.wait()


    async def release_sticky_endpoint(self, endpoint:str):
        """Release the sticky endpoint so that other ProxySessions can use it."""
        async with self.endpoint_lock:
            try:
                self.endpoints.in_use.remove(endpoint)
            except KeyError as e:
                logger.error(e)
                raise e
            self.endpoint_condition.notify()


    async def create_proxy_session(self, stateful:bool=False) -> ProxySession:
        """Factory method for creating ProxySession objects.
        First get a proxy endpoint based on stateful or not. 
        Then create the ProxySession, passing in the
        manager interface object so that the proxy session can query/update the 
        proxy manager.
        """
        if stateful:
            endpoint = await self.get_sticky_endpoint()
        else:
            endpoint = self.endpoints.rotating
        return ProxySession(
            endpoint=f"http://{endpoint}",
            manager_interface=self.session_manager_interface,
        )
        
