import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist
# from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional

from webweaver.auth.authentication import AuthRoute
from webweaver.auth.models import User

from webweaver.common.utils import populate_table_from_enum
from webweaver.config import PROXY

from webweaver.schema.pydantic_schemas import (
    SpiderAssetSchema, 
    SpiderAssetDetailSchema, 
    LaunchCampaignSchema, 
    LaunchSpiderSchema, 
    SpiderAssetIdSchema,
    CreateParamsSchema
)
from webweaver.scripts.create_module_files import create_spider_module_files

from webweaver.exceptions import CampaignBuilderError
from webweaver.webscraping.registry.scraping_registry import scraping_registry, CampaignBuilder, SoloSpiderBuilder
from webweaver.webscraping.spiders.spider_launcher import SpiderLauncher
from webweaver.webscraping.middleware.middleware_manager import MiddlewareManager
from webweaver.webscraping.pipelines.pipeline_listener import PipelineListener
from webweaver.webscraping.proxy.proxy_manager import ProxyManager, SpiderProxyManagerInterface

from webweaver.webscraping.spiders.models import SpiderAsset, SpiderParameter

from webweaver.webscraping.campaigns.models import ScrapeJob
from webweaver.webscraping.outfile.outfile_base import OutFileData, OutFile
from webweaver.webscraping.webscrape import WebScrape


logger = logging.getLogger('scraping')
router = APIRouter()


@router.post("/jobs/save")
async def save_job(input:LaunchCampaignSchema):
    # from webscraping.models import ScrapeModel

    # # job = await ScrapeJob.get_or_none(id=input.id)
    job = await ScrapeJob.get_or_none(id=input.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Can not save job.")


    # tables = await job.tables.all()
    # print([table.table_name for table in tables])
    outfile_data = OutFileData(job, file_format=input.file_format)
    await outfile_data.build()
    # print(outfile_data.dataframes)

    outfile = OutFile(outfile_data)
    await outfile.save()

    return{"Status code":200}



@router.post("/launch_project")
# async def launch_spider(launch_data:LaunchSpiderSchema, user:User = Depends((AuthRoute.spider_launch))):
async def launch_project(launch_data:LaunchSpiderSchema):

    webscrape = WebScrape()
    # await webscrape.scrape(launch_data, is_proxy=False, is_campaign=False)
    await webscrape.scrape(
        launch_data, 
        is_proxy=True, 
        is_campaign=False,
        project_id=1
    )

    return {"asdffdsa": "fdafdsaf scrapppe"}




@router.post("/launch_campaign")
async def launch_campaign(launch_data:LaunchCampaignSchema, user:User = Depends((AuthRoute.spider_launch))):
# async def launch_campaign(launch_input:LaunchInputSchema):

    webscrape = WebScrape()
    await webscrape.scrape(launch_data, is_proxy=False, is_campaign=True)
    # await webscrape.scrape(launch_data, is_proxy=True, is_campaign=True)

    return {"asdffdsa": "fdafdsaf scrapppe"}


@router.post("/launch_spider")
# async def launch_spider(launch_data:LaunchSpiderSchema, user:User = Depends((AuthRoute.spider_launch))):
async def launch_spider(launch_data:LaunchSpiderSchema):

    webscrape = WebScrape()
    # await webscrape.scrape(launch_data, is_proxy=False, is_campaign=False)
    await webscrape.scrape(launch_data, is_proxy=True, is_campaign=False)

    return {"asdffdsa": "fdafdsaf scrapppe"}


@router.post("/test_spider")
async def test_spider(spider_id: SpiderAssetIdSchema):

    from playwright.async_api import async_playwright
    from webscraping.spiders.spider_base import Spider

    # middleware_manager = MiddlewareManager()
    proxy_manager = ProxyManager()
    sa = await SpiderAsset.get_or_none(id=spider_id.id)

    logger.info(f">>>> Testing {sa.spider_name}Spider")
    SpiderClass = sa.get_spider()

    if SpiderClass is not None:
        p = await async_playwright().start()
        spider:Spider = SpiderClass(
            spider_asset=sa,
            proxy_manager_interface = proxy_manager.spider_manager_interface,
            p=p,
            test_env=True
            )
        await spider.run()
        await p.stop()



@router.post("/create_params")
async def create_params(data:CreateParamsSchema):
    """Create the parameters in new_spider.py script."""

    spider = await SpiderAsset.get(id=data.spider_id)
    param_objects = [
        SpiderParameter(
            spider_id = spider,
            param_name = param.param_name,
            param_type = param.param_type.lower(),
            param_description = param.param_description
        ) for param in data.params
    ]
    async with in_transaction():
        await SpiderParameter.bulk_create(param_objects)


@router.post("/create_spider")
async def create_spider(data:dict):
    schema = SpiderAssetSchema(**data['spider_asset'])
    spider_type = data['spider_module']['spider_type']
    if await SpiderAsset.exists(spider_name=schema.spider_name):
        raise HTTPException(status_code=400, detail="Failed to create spider")
    spider_data = schema.model_dump()
    del spider_data['id']
    sa = SpiderAsset(**spider_data)
    await sa.save()
    create_spider_module_files(sa, spider_type)

    return {"spider_id": sa.id}


@router.get("/listSpiders")
async def list_spiders(spider_id: Optional[int]=None):

    if spider_id:
        sa = await SpiderAsset.get_or_none(id=spider_id).values("id", "spider_name", "domain", "description", "is_active")
        if not sa:
            raise HTTPException(status_code=404, detail="Spider not found")
        params = await SpiderParameter.filter(spider_id=spider_id).values("param_name", "param_type", "param_description")       
        if params:
            sa['params'] = params
        else:
            sa['params'] = None
        validated_data = SpiderAssetDetailSchema(**sa)
        return validated_data
    else:
        spiders = await SpiderAsset.all()
        return [SpiderAssetSchema(
            id=spider.id,
            spider_name=spider.spider_name, 
            is_active=spider.is_active, 
            domain=spider.domain, 
            description=spider.description
        ) for spider in spiders]




# @router.get("/populate_table")
# async def init_db():
#     await populate_table_from_enum()
#     print('okayyyyy')
#     return {'bleh':'blah'}

