from __future__ import annotations
import logging
from pydantic import BaseModel#, ValidationError
from pydantic_core import ValidationError
from tortoise.transactions import atomic
from tortoise.models import Model
from typing import TYPE_CHECKING

# from webscraping.pipelines.pipeline_cleaner import PipelineCleaner
from webweaver.exceptions import SchemaValidationError, MethodNotSubclassed, SchemaNotFound
from webweaver.project.project_base import ProjectHandler
from webweaver.webscraping.registry.scraping_registry import scraping_registry, SpiderState
from webweaver.webscraping.spiders.spider_data import SpiderData#, SpiderDataBatch



if TYPE_CHECKING:
    from webweaver.webscraping.spiders.spider_base import SpiderAsset


logger = logging.getLogger("scraping")


class Pipeline:

    schema = None #override this in child class with pydantic schema

    def __init__(self, spider_asset:"SpiderAsset", spider_data:SpiderData, project_handler:ProjectHandler=None):
        # self.spider_id:int = spider_data.spider_id
        self.spider_data = spider_data
        self.spider_asset = spider_asset
        self.data_to_save = None
        self.project_handler = project_handler


    def get_spider_asset(self) -> "SpiderAsset":
        return scraping_registry.get_spider_asset(self.spider_asset.id)


    async def validate_data(self):
        if self.schema is None:
            message = f"SchemaNotFound({self.__class__.__name__})"
            logger.error(SchemaNotFound(message))
            await scraping_registry.set_spider_state(self.spider_asset.id, SpiderState.ERROR)
            return
        else:        
            self.data_to_save = await self.validate(self.spider_data.data, self.schema)


    async def save_data(self):
        """Subclass this method to write pipeline DB-saving logic"""
        spider_name = scraping_registry.get_spider_name(self.spider_asset.id)
        logger.error(repr(MethodNotSubclassed(f"{spider_name} has no save_data() method!")))
        return


    def _validate(self, data:dict, schema:BaseModel) -> BaseModel:
        """Validate the scraped data against the appropriate pydantic schema"""
        # print(data)
        # print('='*50)
        # print(schema)
        # print()
        instance = schema(**data)
        return instance


    def _validate_or_log(self, data:dict, schema:BaseModel) -> BaseModel:
        """Wrapper for self._validate method to log error."""
        try:
            return self._validate(data, schema)
        except ValidationError as e:
            logger.error(e.errors())
            logger.error(f"ValidationError count: {e.error_count()}")
            print()
            print('==================')
            for key, value in data.items():
                print(key, " : ", value)
            print('==================')
            print()
            raise SchemaValidationError


    async def validate(self, data:dict, schema:BaseModel):
        """If SchemaValidationError is raised by self._validate_or_log, 
        this method will update the spider's state so it will not continue 
        scraping.
        """
        try:
            return self._validate_or_log(data, schema)
        except SchemaValidationError:
            await scraping_registry.set_spider_state(self.spider_asset.id, SpiderState.ERROR)

        return
    