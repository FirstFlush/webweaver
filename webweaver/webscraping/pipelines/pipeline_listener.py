import asyncio
import logging
from pathlib import Path
from pydantic import ValidationError
import traceback
from tortoise.exceptions import TransactionManagementError, IntegrityError

from webweaver.config import SENTINEL
from webweaver.project.project_base import ProjectHandler
from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.webscraping.registry.scraping_registry import scraping_registry
from webweaver.webscraping.spiders.spider_data import SpiderData#, SpiderDataBatch, BatchRegistry


logger = logging.getLogger("scraping")


class PipelineListener:
    """This class handles listening to the queue for scraped data, 
    and then passing it to the appropriate Pineline subclass.
    """

    def __init__(self, queue:asyncio.Queue, project_handler:ProjectHandler=None):
        self.queue = queue
        self.sentinel = SENTINEL
        # self.batch_registry = BatchRegistry()
        self.project_handler = project_handler


    def get_spider_asset(self, spider_id:int) -> SpiderAsset:
        """Returns the SpiderAsset from the spider registry"""
        return scraping_registry.registry[spider_id].spider_asset


    def get_pipeline_object(self, sa:SpiderAsset, spider_data:SpiderData=None) -> Pipeline | None:
        """Retrieves the pipeline class for the SpiderAsset"""
        pipeline = None
        if self.project_handler:
            PipelineClass = self.project_handler.pipeline_class
        else:
            PipelineClass = sa.get_pipeline()
        if PipelineClass:
            pipeline = PipelineClass(spider_asset=sa, spider_data=spider_data, project_handler=self.project_handler)
        return pipeline


    async def process_pipeline_data(
            self, 
            spider_data:SpiderData
    ):
        """Retrieve the pipeline object and process the batch of data."""
        spider_asset = self.get_spider_asset(spider_data.spider_id)
        pipeline = self.get_pipeline_object(sa=spider_asset, spider_data=spider_data)
        if pipeline is not None:
            await pipeline.validate_data()
            try:
                await pipeline.save_data()
            except Exception as e:
                # print('data to save in pipeline listener: ')
                logger.error(f"{e.__class__.__name__} ({spider_asset.spider_name})")
                print('oopsie')
                traceback.print_exception(e)
                # print("FAILED: ", pipeline.data_to_save.product.product_name)
        # spider_data_batch.reset_batch()
        return


    # async def record_validation_error(self, e:ValidationError, spider_module_path:Path):
    #     """Called when the data sent to the pipeline module fails its 
    #     schema validation and raises a pydantic ValidationError.
    #     """
    #     with open(f"{spider_module_path}/{Path('validation_errors.txt')}", "a") as f:
    #         f.write(e.errors())
    #         f.write("\n")


    # async def process_leftover_pipeline_data(self):
    #     """Process remaining batch data.. for the leftover batches that didn't
    #     hit the batch_size_limit threshold.
    #     """
    #     for spider_id, spider_data_batch in self.batch_registry.batches.items():
    #         if spider_data_batch.count() > 0:
    #             spider_asset = self.get_spider_asset(spider_id)
    #             await self.process_pipeline_batch(spider_asset, spider_data_batch)
    #     return


    async def listen(self):
        """Checking the queue for data and instantiating the 
        appropriate Pipeline subclass for processing.
        """
        while True:
            spider_data:SpiderData = await self.queue.get()
            if spider_data == self.sentinel:
                logger.info("Pipeline sentinel value received")
                break

            # self.batch_registry.add_data(spider_data)
            # if self.batch_registry.is_batch_full(spider_data.spider_id):
            #     spider_data_batch = self.batch_registry.batches[spider_data.spider_id]
            # spider_asset = self.get_spider_asset(spider_data.spider_id)
            # data = spider_data.data
            await self.process_pipeline_data(spider_data)  

        # await self.process_leftover_pipeline_data()

        logger.info("Pipeline terminated")
