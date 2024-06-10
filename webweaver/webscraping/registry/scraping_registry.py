from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from asyncio import Lock
import logging
from typing import Optional
# from tortoise.exceptions import DoesNotExist
from webweaver.webscraping.registry.builders import CampaignBuilder, SoloSpiderBuilder
from webweaver.webscraping.campaigns.models import Campaign, ScrapeJob
from webweaver.webscraping.spiders.models import SpiderAsset, ScrapeModuleTable


logger = logging.getLogger('scraping')
lock = Lock()


class SpiderState(Enum):
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


@dataclass
class SpiderRegistryItem:
    spider_asset: SpiderAsset
    params: dict[str, str]
    state: SpiderState


class ScrapingRegistry:
    """This class serves as a shared state between diferent parts of the app.
    For example if a pipeline module encounters an error and wants to tell a spider module
    to stop scraping, it can inform the spider by updating the spider's state in the ScrapingRegistry. 
    The Spider can check this state periodically as it scrapes.

    Example self.registry:
    {
        1: SpiderRegistryItem(spider_asset=ABCSpider, params={"search":"bakeries, NY"}, SpiderState.RUNNING)
        8: SpiderRegistryItem(spider_asset=XYZSpider, params={"dir_path":"/search/newyork"}, SpiderState.COMPLETE)
    }
    -The keys (ints) are the SpiderAsset IDs. The values are the SpiderAssets and their states.
    -Spider's check_state() method checks the state and Pipeline's update_state() updates it.
    """
    registry: dict[int, SpiderRegistryItem] = {}
    campaign: Optional[Campaign] = None
    scrape_job: Optional[ScrapeJob] = None
    spiders: list[SpiderAsset] = None
    scrape_table_names:list[str] = []
    scrape_table_models:list[ScrapeModuleTable] = []

    async def build(self,
            campaign_builder: CampaignBuilder = None,
            solospider_builder: SoloSpiderBuilder = None,
    ):
        if campaign_builder:
            self.add_campaign(campaign_builder.campaign)
            self.add_scrape_job(campaign_builder.scrape_job)
            self.add_spiders(campaign_builder.spider_details)
            self.spiders = self.create_spider_list(campaign_builder.spider_details)
        elif solospider_builder:
            self.add_scrape_job(solospider_builder.scrape_job)
            self.add_spiders(solospider_builder.spider_details)  
            self.spiders = self.create_spider_list(solospider_builder.spider_details)
        
        self.scrape_table_names = self._table_names()
        self.scrape_table_models = await self._table_models()
        await self.record_scrape_tables()
        # await self.increase_scrape_count()


    def create_spider_list(self, spider_details: list) -> list[SpiderAsset]:
        return [spider['spider'] for spider in spider_details]


    def _table_names(self) -> list[str]:
        """Gets the names of the scraping module tables used in this scrape job."""
        table_names = set()
        for spider in self.spiders:
            for table_name in spider.table_names():
                table_names.add(table_name)
        return list(table_names)


    async def _table_models(self) -> list[ScrapeModuleTable]:
        """Gets the ScrapeModuleTable associated with the respective names
        in self.scrape_table_names
        """
        return await ScrapeModuleTable.get_tables(self.scrape_table_names)


    async def record_scrape_tables(self):
        """Add the scrape module tables to the scrape job, so that the scraped
        data can be easily referenced from the ScrapeJob object.
        """
        await self.scrape_job.add_tables_to_scrape_job(self.scrape_table_models)
        return
    
    # def add_table(self, table_name:str):
    #     """Adds the table name to the self.scrape_tables set."""
    #     self.scrape_tables.add(table_name)


    async def increase_scrape_count(self, scrape_finished:bool=False):
        """Increase the scrape_start_count of the tables by 1. 
        If scrape_finished=True, increase the scrape_finish_count 
        by 1 instead.
        #TODO function not in use because it gave me weird problems:
        pypika.utils.CaseException: At least one 'when' case is required for a CASE statement.
        """
        for instance in self.scrape_table_models:
            if scrape_finished:
                instance.scrape_finish_count += 1
            else:
                instance.scrape_start_count += 1  
        if scrape_finished:
            await ScrapeModuleTable.bulk_update(self.scrape_table_models, ['scrape_finish_count'])
        else:
            await ScrapeModuleTable.bulk_update(self.scrape_table_models, ['scrape_start_count'])


    def add_spider(
            self,
            spider_id: int,
            spider_asset: SpiderAsset,
            params: dict[str, str],
            state: SpiderState = SpiderState.RUNNING
    ):
        self.registry[spider_id] = SpiderRegistryItem(
            spider_asset, params, state)


    def add_spiders(self, spider_details: list):
        """Adds the spiders and their respective parameters to the registry"""
        for spider_detail in spider_details:
            spider = spider_detail['spider']
            params = spider_detail['params']
            self.add_spider(
                spider_id=spider.id,
                spider_asset=spider,
                params=params
            )


    def add_scrape_job(self, scrape_job:ScrapeJob):
        self.scrape_job = scrape_job


    def add_campaign(self, campaign:Campaign):
        """Adds the Campaign object to the registry."""
        self.campaign = campaign
        return

    def _get_sri(self, spider_id: int) -> SpiderRegistryItem:
        """Grab a SpiderRegistryItem based on the SpiderAsset's id."""
        return self.registry[spider_id]

    def get_spider_asset(self, spider_id:int) -> SpiderAsset:
        """Grab a SpiderAsset object from the registry."""
        return self.registry[spider_id].spider_asset


    async def spider_error(self, spider_id:int):
        """When a spider causes pipeline errors, the pipeline listener can
        set the spider's state the ERROR to stop webscraping from proceeding.
        """
        async with lock:
            self._get_sri(spider_id).state = SpiderState.ERROR

    async def set_spider_state(self, spider_id: int, state: SpiderState):
        async with lock:
            self._get_sri(spider_id).state = state

    def get_spider_name(self, spider_id: int) -> str:
        return self._get_sri(spider_id).spider_asset.spider_name

    def get_spider_state(self, spider_id: int) -> SpiderState:
        return self._get_sri(spider_id).state


    async def roll_back(self):
        """Deletes the ScrapeJob (and all associated scraped data!) 
        if saving the db fails in any way.
        """
        try:
            await self.scrape_job.delete()
        except AttributeError:
            pass
        self.scrape_job = None


    async def finish(self):
        """Scrape job finished successfully!
        Increase the scrape_finish_count of all the tables, 
        and clear the registry.
        """
        async with lock:
            # await self.increase_scrape_count(scrape_finished=True)
            self.clear()
            logger.info("Scraping successful")
            logger.info("Scraping registry cleared")


    def clear(self):
        """Sets all the registry's values to defaults, thus clearing the registry."""
        self.campaign = None
        self.registry = {}
        self.scrape_job = None
        self.spiders = None
        self.scrape_table_names = []
        self.scrape_table_models = []
        return


scraping_registry = ScrapingRegistry()
