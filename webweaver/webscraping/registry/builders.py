import logging

# from common.utils import instance_to_dict

from webweaver.exceptions import CampaignBuilderError, SpiderAssetNotFound
from webweaver.schema.pydantic_schemas import LaunchSpiderSchema, LaunchCampaignSchema
from webweaver.webscraping.campaigns.models import Campaign, ScrapeJob, ParameterValue
from webweaver.webscraping.spiders.models import SpiderAsset


logger = logging.getLogger('scraping')

            # d = {
            #     'spider': spider,
            #     'params': {}
            # }
            # param_keys = await spider.params.all()
            # for param_key in param_keys:
            #     param_value = await ParameterValue.get(parameter_id=param_key, campaign_id=self)
            #     d['params'][param_key.param_name] = param_value.value
            # spider_details.append(d)


class Builder:
    
    async def _create_scrape_job(self, campaign:Campaign=None, scrape_job_id:int=None) -> ScrapeJob:
        """Creates or retrieves a ScrapeJob object."""
        if campaign:
            return await ScrapeJob.create(campaign_id=campaign)
        elif scrape_job_id:
            scrape_job = await ScrapeJob.get_or_none(id=scrape_job_id)
            if scrape_job:
                return scrape_job
        return await ScrapeJob.create()


class SoloSpiderBuilder(Builder):

    def __init__(self, launch_data:LaunchSpiderSchema):
        self.spider_details = []
        self.campaign = None
        self.spider_id = launch_data.id
        self.scrape_job_id = launch_data.scrape_job_id
        self.spider_asset:SpiderAsset = None
        self.scrape_job:ScrapeJob = None
        self.file_format = launch_data.file_format
        self.params = {}
        params_list = [param.model_dump() for param in launch_data.params]
        for param in params_list:
            self.params[param['param_name']] = param['param_value']

    async def initialize_solo_scrape(self):
        self.spider_asset = await self._get_spider_asset()
        self.scrape_job = await self._create_scrape_job(scrape_job_id=self.scrape_job_id)
        self.build_spider_details()

    def build_spider_details(self):
        d = {
            'spider': self.spider_asset,
            'params': self.params
        }
        self.spider_details.append(d)

    async def _get_spider_asset(self) -> SpiderAsset:
        """Returns the SpiderAsset for scraping."""
        spider_asset = await SpiderAsset.get_or_none(id=self.spider_id)
        if spider_asset is None:
            logger.error(f"SpiderAssetNotFound: SingleSpiderScrapeBuilder could not find spider asset with id '{self.spider_id}'")
            raise SpiderAssetNotFound
        return spider_asset


class CampaignBuilder(Builder):
    """This class takes gathers & builds the data required to 
    launch a campaign:
    fetches from DB:
        -campaign object
        -spiders in campaign
            -parameters
            -parameter values
    creates in DB:
        -scrapejob object
    """
    def __init__(self, launch_data:LaunchCampaignSchema):
        self.campaign_id = launch_data.id
        self.file_format = launch_data.file_format
        self.campaign = None
        self.spider_details = None
        self.scrape_job = None


    @classmethod
    async def build_campaign(cls, launch_data:LaunchCampaignSchema) -> "CampaignBuilder":
        builder = CampaignBuilder(launch_data)
        try:
            builder.campaign = await builder._get_campaign_object()
        except CampaignBuilderError as e:
            logger.error(f"{e.__class__.__name__}: Could not build campaign with campaign id '{launch_data.id}'")
            raise e
        builder.spider_details = await builder._get_spider_details()
        builder.scrape_job = await builder._create_scrape_job(builder.campaign)
        return builder




    async def _get_campaign_object(self) -> Campaign:
        campaign = await Campaign.get_or_none(id=self.campaign_id)
        if campaign is None:
            raise CampaignBuilderError
        return campaign

    async def _get_spider_details(self):
        spider_details = await self.campaign.campaign_spider_details()
        if len(spider_details) == 0:
            raise CampaignBuilderError
        return spider_details