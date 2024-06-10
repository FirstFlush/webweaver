import logging

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from pathlib import Path
from typing import Optional

from webweaver.auth.authentication import AuthRoute
from webweaver.auth.models import User
from webweaver.common.utils import instance_to_dict
from webweaver.config import TEMPLATES, ROUTES, templates

from webweaver.routes.common_dependencies import (
    get_spider_by_id_or_none,
    get_campaign_by_id_or_none,
    get_job_by_id_or_none,
    list_campaign,
)
from webweaver.webscraping.campaigns.forms import ChooseSpiderForm
from webweaver.webscraping.campaigns.models import Campaign, ScrapeJob
from webweaver.webscraping.spiders.models import SpiderAsset, SpiderParameter
from webweaver.webscraping.models import ScrapeModel
from webweaver.schema.pydantic_schemas import (
    CampaignSchema, 
    CampaignIdSchema,
    CampaignsSchema, 
    JobSchema, 
    JobsSchema, 
    SpiderAssetIdSchema, 
    SelectParamsSchema
)

router = APIRouter()

@router.get("/campaign_details")
async def campaign_details(campaign:Campaign = Depends(get_campaign_by_id_or_none)):
    
    campaign_data = await campaign.campaign_data()
    validated_data = CampaignSchema(**campaign_data)
    campaign_dir = campaign.campaign_dir()
    json_data = validated_data.model_dump_json()
    json_file = campaign_dir/Path('campaign_data.json')
    json_file.write_text(json_data, encoding='utf-8')

    return CampaignSchema(**campaign_data)


@router.get("/list_params")
async def select_params(spider_asset_id:int = Depends(SpiderAssetIdSchema)):

    spider_asset = await SpiderAsset.get_or_none(id=spider_asset_id.id)
    if spider_asset is None:
        raise HTTPException(status_code=404, detail="Can not get params for spider with that id.")
    select_params_data = {}
    select_params_data['spider_name'] = spider_asset.spider_name
    params = await spider_asset.params.all()
    select_params_data['params'] = [instance_to_dict(param) for param in params]

    validated_data = SelectParamsSchema(**select_params_data)
    return validated_data


@router.get("/list_jobs")
# async def list_jobs(job_id:Optional[int]=None, last:bool=False):
async def list_jobs(scrape_job:ScrapeJob = Depends(get_job_by_id_or_none)):

    if scrape_job:
        data = instance_to_dict(scrape_job)
        campaign = scrape_job.campaign_id
        scraped_data = await scrape_job.scraped_data(ScrapeModel.__subclasses__())
        data['scraped_records'] = scrape_job.count_records(scraped_data)
        tables = await scrape_job.tables.all()
        data['tables'] = [instance_to_dict(table) for table in tables]
        if campaign:
            data['campaign'] = instance_to_dict(campaign)
        else:
            data['campaign'] = None
        validated_data = JobSchema(**data)

        return validated_data

    else:        
        jobs_data = []
        jobs = await ScrapeJob.filter(is_error=False).prefetch_related('campaign_id')
        for job in jobs:
            data = instance_to_dict(job)
            campaign = job.campaign_id
            if campaign:
                data['campaign_id'] = job.campaign_id.id
            else:
                data['campaign_id'] = None
            jobs_data.append(data)
        return [JobsSchema(**job) for job in jobs_data]


@router.get("/list_campaigns")
# async def list_campaigns(campaign_id:Optional[int]=None):
async def list_campaigns(campaign:Campaign = Depends(list_campaign)):
    if not campaign:
        campaigns = await Campaign.all()
        return [CampaignsSchema(**instance_to_dict(campaign)) for campaign in campaigns]
    else:
        campaign_data = await campaign.campaign_data()        
        validated_data = CampaignSchema(**campaign_data)
        return validated_data



@router.get("/choose_spiders")
# async def create_new(request:Request, user:User = Depends((AuthRoute.create_campaign))):
async def view_spiders(request: Request):
    param_types = SpiderParameter.get_param_types()
    spiders = await SpiderAsset.all()
    context = {
        "spiders": spiders,
        "param_types": param_types,
    }
    return templates.TemplateResponse(TEMPLATES.CHOOSE_CAMPAIGN_SPIDERS, {"request":request, **context})


@router.post("/choose_spiders")
# async def create_new_post(form_data: CreateCampaignForm = Depends(get_form_data)):
async def choose_spiders(request: Request):
    
    form_data = await request.form()
    spider_names = form_data.getlist('spiders')
    campaign_name = form_data.get('campaign_name')

    validated_data = ChooseSpiderForm(campaign_name=campaign_name, spider_names=spider_names)
    fetched_spiders = await SpiderAsset.get_spiders_from_list_of_names(validated_data.spider_names)
    if not await SpiderAsset.compare_names_from_list(validated_data.spider_names, fetched_spiders):
        raise HTTPException(status_code=400, detail="Please choose valid & active spiders.")

    spider_params_dicts = {spider:await spider.params for spider in fetched_spiders}
    context = {
        'spider_params_dicts': spider_params_dicts,
        'campaign_name': campaign_name,
    }
    return templates.TemplateResponse(TEMPLATES.CHOOSE_CAMPAIGN_PARAMS, {"request":request, **context})


@router.post("/choose_params")
async def choose_params(request: Request):

    form_data = await request.form()
    campaign_name = form_data.get('campaign_name')
    params = {key: value for key, value in form_data.items() if key != "campaign_name"}

    campaign = await Campaign.create_campaign(campaign_name, params)
    campaign_data = await campaign.campaign_data()
    validated_data = CampaignSchema(**campaign_data)
    campaign_dir = campaign.campaign_dir()
    campaign.campaign_data_dir()
    json_data = validated_data.model_dump_json()
    json_file = campaign_dir/Path('campaign_data.json')
    json_file.write_text(json_data, encoding='utf-8')

    return validated_data
