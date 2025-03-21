# from __future__ import annotations
import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright
from playwright.async_api._generated import Playwright as AsyncPlaywright
from typing import Optional

from webweaver.config import SENTINEL, ACCEPTABLE_SPIDER_DURATION, RETURN_EXCEPTIONS
from webweaver.webscraping.spiders.models import SpiderAsset, SpiderError
from webweaver.exceptions import BrokenSpidersError, WebScrapingError

from webweaver.webscraping.middleware.middleware_manager import SpiderMiddlewareManagerInterface
from webweaver.webscraping.proxy.proxy_manager import SpiderProxyManagerInterface
from webweaver.webscraping.spiders.spider_base import Spider, PlaywrightSpider
from webweaver.webscraping.spiders.spider_data import SpiderData


logger = logging.getLogger("scraping")


class BrokenSpider:

    def __init__(self, spider_asset_id:int, error:Exception):
        self.spider_asset_id = spider_asset_id
        self.error = error.__class__.__name__
        self.time = datetime.utcnow()


class SpiderLauncher:
    """Class From which we launch the spiders asynchronously 
    and feed them into the database pipeline.
    """
    def __init__(
            self, 
            queue:asyncio.Queue, 
            spiders:list[SpiderAsset],
            middleware_manager_interface:SpiderMiddlewareManagerInterface,
            proxy_manager_interface:SpiderProxyManagerInterface
            ):
        self.spiders = spiders
        # self.spiders = [spider for spider in self.spiders if spider.id == 3] 

        self.spider_count = len(self.spiders)
        # self.broken_spiders:list[tuple] = []
        self.broken_spiders:list[BrokenSpider] = []
        self.middleware_manager_interface = middleware_manager_interface
        self.proxy_manager_interface = proxy_manager_interface
        self.p = None  # AyncPlaywright
        self.queue = queue
        self.sentinel = SENTINEL


    def spider_broke(self, spider_asset_id:int, error:WebScrapingError):
        """When a spider fails, append the spider ID
        to self.broken_spiders
        """
        bs = BrokenSpider(spider_asset_id, error)
        self.broken_spiders.append(bs)

        return


    async def send_to_queue(self, spider_id:int, data:dict):
        """Pass a spider's scraped data into the asyncio Queue, 
        to be consumed by the PipelineListener
        """
        if bool(data):
            sd = SpiderData(data=data, spider_id=spider_id)
            await self.queue.put(sd)
        return


    async def close_queue(self):
        """Closes the async Queue by passing in the sentinel value."""
        logger.debug("Sending sentinel value to PipelineListener...")
        await self.queue.put(self.sentinel)


    async def start_playwright(self):
        """Launches Async Playwright and returns its instance. Each 
        spider will create its own browser/context/pages, but the 
        SpiderLauncher will start/stop Playwright. 
        """
        self.p = await async_playwright().start()
        logger.debug("Playwright starting...")

        # print('any: ', any(issubclass(spider.__class__, PlaywrightSpider) for spider in self.spiders))
        # if any(issubclass(spider.__class__, PlaywrightSpider) for spider in self.spiders):
        #     self.p = await async_playwright().start()
        #     logger.debug("Starting playwright")
        #     print('asdfjkdsajfkladsjfklads')
        return


    def record_timing(self, start:datetime):
        """Function displaying how long the spiders took to 
        finish scraping.
        """
        end = datetime.now()
        logger.info(f"{end.strftime('%H:%M:%S.%f')} Scraping complete")
        time_elapsed = end - start
        time_str = f"\033[1m{time_elapsed}\033[0m to complete"
        if time_elapsed.seconds < ACCEPTABLE_SPIDER_DURATION:
            logger.info(time_str)
        else:
            logger.warning(time_str)
        return


    async def launch(self): 
        """Iterates through all the spiders and calls launch_spider()"""
        tasks = []
        await self.start_playwright()
        start_time = datetime.now()
        logger.info(f"{start_time.strftime('%H:%M:%S.%f')} Launching {len(self.spiders)} spiders...")
        for spider in self.spiders:
            task = asyncio.create_task(self.launch_spider(spider))
            logger.debug(f">>>> {spider.spider_name}Spider launched")
            tasks.append(task)
        # await asyncio.gather(*tasks, return_exceptions=RETURN_EXCEPTIONS)
        await asyncio.gather(*tasks, return_exceptions=False)
        await self.close_queue()
        self.record_timing(start_time)
        if len(self.broken_spiders) > 0:
            self.log_errors()
            await self.record_errors()
        else:
            logger.info(f"Broken spiders: 0")
        await self.stop_playwright()
        return


    async def launch_spider(self, sa:SpiderAsset):
        """Dynamically import the spider module and instantiate the class
        associated with spider_name. Spiders are configured to run on
        instantiation.
        """
        SpiderClass = sa.get_spider()
        if SpiderClass is not None:
            p = self.p if self.is_playwright_spider(SpiderClass) else None
            spider:Spider = SpiderClass(
                spider_asset = sa,
                middleware_manager_interface = self.middleware_manager_interface,
                proxy_manager_interface = self.proxy_manager_interface,
                p=p
            )
            async for scraped_data in spider.run():
                if spider.check_state():
                    await self.send_to_queue(
                        spider_id=sa.id, 
                        data=scraped_data
                    )
                else:
                    logger.warning(f"{sa.spider_name} SpiderState: {spider.get_state().value}")
                    await spider.aio.close_session()                    
                    return spider.sentinel
            # if spider.is_error == True:
            #     self.spider_broke(sa.id, spider.error)
            #     logger.error(f"\033[1mBROKEN SPIDER\033[0m - {sa.spider_name}")

        return


    def is_playwright_spider(self, SpiderClass:Spider) -> bool:
        """Checks if the spider inherits from the PlaywrightSpider class"""
        return issubclass(SpiderClass, PlaywrightSpider)


    async def stop_playwright(self):
        """Shuts down playwright and the webdriver"""
        if self.p is not None:
            logger.debug("Playwright stopped")
            await self.p.stop()
        return


    def log_errors(self):
        """Creates a BrokenSpiders log entry"""
        num = len(self.broken_spiders)
        logger.error(repr(BrokenSpidersError(f"{num} broken spider{'' if num==1 else 's'}")))
        return


    async def record_errors(self):
        """Creates a SpiderError object in the DB for each of 
        the spiders in self.broken_spiders
        """
        spider_errors = [SpiderError(spider_id_id=bs.spider_asset_id, error=bs.error, date_logged=bs.time) for bs in self.broken_spiders]
        await SpiderError.bulk_create(spider_errors)
        return


