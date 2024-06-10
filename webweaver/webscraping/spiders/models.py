from __future__ import annotations
import importlib
import logging
import toml
from pathlib import Path
from typing import Awaitable, List, TYPE_CHECKING

from tortoise.models import Model
from tortoise import fields

from webweaver.common.enums import ParamTypeEnum
from webweaver.common.fields import DomainField
from webweaver.common.utils import instance_to_dict
from webweaver.config import SCRAPING_MODULES, SCRAPING_MODULES_DIR
from webweaver.exceptions import (
    SpiderModuleNotFound, 
    PipelineModuleNotFound,
    ConfigModuleNotFound,
    ConfigModelsNotFound,
)
# from webscraping.pipelines.pipeline_base import Pipeline
# from webscraping.spiders.spider_base import Spider
if TYPE_CHECKING:
    from webweaver.webscraping.spiders.spider_base import Spider
    from webweaver.webscraping.pipelines.pipeline_base import Pipeline


logger = logging.getLogger('scraping')


class SpiderAsset(Model):

    spider_name         = fields.CharField(max_length=255)
    domain              = DomainField(max_length=255)
    description         = fields.TextField(max_length=2048)
    is_active           = fields.BooleanField(default=True)
    is_search_string    = fields.BooleanField(default=False)
    date_modified       = fields.DatetimeField(auto_now=True)
    date_created        = fields.DatetimeField(auto_now_add=True)


    @property
    def module_config(self) -> dict:
        """Returns the spider's config.toml file data as a dict."""
        config_path = self.module_dir_path() / Path("config.toml")
        try:
            return toml.load(config_path)
        except (FileNotFoundError, toml.TomlDecodeError, TypeError) as e:
            logger.error(ConfigModuleNotFound(e))
            raise ConfigModuleNotFound(e)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._module_config = None


    def __str__(self):
        return self.spider_name


    # def module_path(self) -> Path:
    #     """Retrieve the full MODULE path to the spider's scraping module"""
    #     return SCRAPING_MODULES / Path(self.spider_name.lower())
    
    def module_path(self) -> str:
        """Retrieve the full MODULE path to the spider's scraping module"""
        return f"{SCRAPING_MODULES}.{self.spider_name.lower()}"
    

    def module_dir_path(self) -> Path:
        """Retrieve the full DIRECTORY path of the spider's scraping module"""
        return SCRAPING_MODULES_DIR / Path(self.spider_name.lower())


    def table_names(self) -> list:
        """Retrieve the table names in the module's .toml config file."""
        try:
            tables = self.module_config['models']['table_names']
        except KeyError:
            pass
        else:    
            if isinstance(tables, list):            
                if len(tables) < 1:
                    logger.warning(f"{self.spider_name}: No models found in config.toml")
                return tables

        raise ConfigModelsNotFound(self.spider_name)
        

    async def get_params(self) -> list[SpiderParameter]:
        return await self.params.all()


    def get_spider(self) -> "Spider" | None:
        """Retrieve the Spider subclass, based on naming convention."""
        SpiderClass = None
        module_name = f"{SCRAPING_MODULES}.{self.spider_name.lower()}.spider"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.error(repr(SpiderModuleNotFound(self.spider_name)))
        else:
            try:
                SpiderClass = getattr(module, f"{self.spider_name}Spider")
            except AttributeError:
                pass

        return SpiderClass


    def get_pipeline(self) -> "Pipeline" | None:
        """Retrieve the Pipeline subclass, based on the same 
        naming convention as self.get_spider()
        """
        PipelineClass = None
        module_name = f"{SCRAPING_MODULES}.{self.spider_name.lower()}.pipeline"
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            logger.error(repr(PipelineModuleNotFound(self.spider_name)))
        else:
            try:
                PipelineClass = getattr(module, f"{self.spider_name}Pipeline")
            except AttributeError:
                pass

        return PipelineClass


    async def activate(self):
        """Activates the spider so it will be loaded into
        the SpiderLauncher
        """
        self.is_active = True
        await self.save()
        return


    async def deactivate(self):
        """Deactivates the spider so it will not be loaded into
        the SpiderLauncher
        """
        self.is_active = False
        await self.save()
        return


    async def errors(self) -> Awaitable[List[SpiderError]]:
        return await self.spider_errors.all()
        

    async def error_count(self) -> int:
        """Get number of errors this spider has generated."""
        return await SpiderError.filter(spider_id=self).count()


    def file_path(self, modules_path:str) -> str:
        """Returns the full file path, assuming the naming convention is:
        Class   SpiderName
        File    spidername.py
        """
        path = f"{modules_path}/{self.spider_name.lower()}.py"
        return path


    @classmethod
    async def get_active(cls) -> Awaitable[List["SpiderAsset"]]:
        """Returns all active Spider assets"""
        spiders = await cls.filter(is_active=True)
        return spiders
    

    @classmethod
    async def get_spiders_from_list_of_names(
        cls, 
        spider_names:list[str]
    ) -> Awaitable[List["SpiderAsset"]]:
        """Returns the active SpiderAsset objects from a list of spider names."""
        return await cls.filter(spider_name__in=spider_names, is_active=True)


    @classmethod
    async def compare_names_from_list(
        cls, 
        spider_names:list[str], 
        fetched_spiders:list["SpiderAsset"] = None
    ) -> bool:
        """Compares fetched spider names with a given list of spider names. 
        If no fetched spiders are provided, the spiders will be fetched from 
        the DB based on the names provided in the list.

        Ultimately this function is checking if all spiders on the list are indeed
        present and active in our DB. This is used when creating a new campaign.
        """
        if fetched_spiders is None:
            fetched_spiders = await cls.get_spiders_from_names(spider_names)
        fetched_spider_names = [spider.spider_name for spider in fetched_spiders]
        return bool(set(fetched_spider_names) == set(spider_names))


class ScrapeModuleTable(Model):

    table_name = fields.CharField(max_length=255)
    scrape_start_count = fields.IntField(default=0)
    scrape_finish_count = fields.IntField(default=0)
    last_scraped = fields.DatetimeField(auto_now=True)


    # async def add_start_count(self):
    #     """Increase the start scrape count by 1."""
    #     self.scrape_start_count += 1
    #     await self.save()


    # async def add_finish_count(self):
    #     """Increase the successfully finished scrape count by 1."""
    #     self.scrape_finish_count += 1
    #     await self.save()


    @classmethod
    async def get_tables(cls, table_names:list[str]) -> list[ScrapeModuleTable]:
        """Retrieves the ScrapeModuleTable instances which have their names in the
        table_names list.
        """
        table_instances = await cls.filter(table_name__in=table_names)
        if len(table_instances) != len(table_names):
            leftover_names = list(set(table_names) - set([table.table_name for table in table_instances]))
            for table_name in leftover_names:
                table_instance = await ScrapeModuleTable.create(table_name=table_name)
                table_instances.append(table_instance)

        return table_instances






class SpiderParameter(Model):

    spider_id           = fields.ForeignKeyField('models.SpiderAsset', related_name='params', on_delete=fields.CASCADE)
    param_name          = fields.CharField(max_length=255)
    param_description   = fields.CharField(max_length=510, null=True)
    param_type          = fields.CharEnumField(ParamTypeEnum)

    class Meta:
        unique_together = ('spider_id', 'param_name')

    @staticmethod
    def get_param_types() -> list:
        """Returns a list of the available parameter types."""
        return list(ParamTypeEnum.__members__.keys())



class SpiderError(Model):

    spider_id = fields.ForeignKeyField('models.SpiderAsset', related_name='spider_errors', on_delete=fields.CASCADE)
    error = fields.CharField(max_length=255)
    date_logged = fields.DatetimeField(auto_now_add=True)