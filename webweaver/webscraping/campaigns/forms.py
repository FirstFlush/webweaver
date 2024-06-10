from pydantic import BaseModel, validator
from typing import List
from fastapi import Form

# from webscraping.spiders.models import SpiderAsset, SpiderParameter

class ChooseSpiderForm(BaseModel):

    campaign_name: str
    spider_names: List[str]
    # @validator('spider_names', pre=True)
    # async def check_spiders_exist(cls, spider_names:list[str]):
    #     fetched_spider_names = [spider.spider_name for spider in await cls.get_spiders_from_names(spider_names)]
    #     return bool(set(fetched_spider_names) == set(spider_names))


