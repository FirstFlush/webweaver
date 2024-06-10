import logging
from datetime import datetime
from pathlib import Path

# from tortoise.models import Model
from tortoise import fields, Model#, Tortoise

from webweaver.common.enums import DaysEnum, FrequenciesEnum
from webweaver.common.utils import instance_to_dict
from webweaver.config import CAMPAIGN_MODULES_DIR, SOLO_SCRAPED_DATA_DIR
from webweaver.webscraping.spiders.models import SpiderAsset, SpiderParameter, ScrapeModuleTable


logger = logging.getLogger('scraping')


class Campaign(Model):

    project_id      = fields.ForeignKeyField('models.Project', related_name='campaigns', null=True, on_delete=fields.SET_NULL)
    campaign_name   = fields.CharField(max_length=255, unique=True)
    spiders         = fields.ManyToManyField("models.SpiderAsset", related_name="campaigns")
    is_recurring    = fields.BooleanField(default=False)
    is_outfile_hook = fields.BooleanField(default=False)
    date_modified   = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)


    @staticmethod
    def check_campaign_name(campaign_name:str|None) -> str:
        """Create campaign name if no name is given."""
        if not bool(campaign_name):
            time = datetime.utcnow()
            campaign_name = time.strftime("campaign__%Y-%m-%d_%H:%M:%S")
        return campaign_name


    async def campaign_data(self) -> dict:
        """Returns dict of the campaign details. This is to be passed 
        into CampaignSchema for validation before being sent out.
        *This method is used when client app lists a single campaign, 
        and when a new campaiagn is created.
        """
        campaign = self
        spiders = await campaign.spiders.all()
        param_values = await campaign.param_values.all()
        campaign_data_spiders = []

        # Iterate through each spider
        for spider in spiders:
            spider_data = instance_to_dict(spider)

            # Get the parameters for the spider
            spider_params = await spider.params.all()
            spider_data_params = []

            # Iterate through each parameter
            for param in spider_params:
                param_data = instance_to_dict(param)
                param_values_for_param = [pv for pv in param_values if await pv.parameter_id == param]
                param_data["param_values"] = [instance_to_dict(pv) for pv in param_values_for_param]
                spider_data_params.append(param_data)
            spider_data["params"] = spider_data_params
            campaign_data_spiders.append(spider_data)

        campaign_data = instance_to_dict(campaign)
        campaign_data["spiders"] = campaign_data_spiders
        return campaign_data


    def campaign_dir(self) -> Path:
        """Returns the file path for the campaign module."""
        campaign_dir_path = f"{CAMPAIGN_MODULES_DIR}/{self.campaign_name.lower()}"
        dir = Path(campaign_dir_path)
        dir.mkdir(exist_ok=True)
        return dir

    def campaign_data_dir(self) -> Path:
        """Creates the directory where the scraped campaign data will be saved to."""
        dir = self.campaign_dir()/Path('scraped_data')
        dir.mkdir(exist_ok=True)
        return dir


    async def campaign_spider_details(self) -> list[dict]:
        """Reurns a list of dictionaries of spiders, with their respective params as sub-dictionaries.
        This is used for building the scraping registry at launch time.
        """
        spiders = await self.spiders.all()
        spider_details = []
        for spider in spiders:
            d = {
                'spider': spider,
                'params': {}
            }
            param_keys = await spider.params.all()
            for param_key in param_keys:
                param_value = await ParameterValue.get(parameter_id=param_key, campaign_id=self)
                d['params'][param_key.param_name] = param_value.value
            spider_details.append(d)

        return spider_details


    @classmethod
    async def create_campaign(cls, campaign_name:str|None, params:dict[str,str]) -> "Campaign":
        """Builds a new Campaign Db object from the user's supplied inputs.
        Example of key, value in params dict:
        ("<spider name>--<param name>", "<param value>")
        """
        name = Campaign.check_campaign_name(campaign_name)
        campaign = await Campaign.create(campaign_name=name)
        spider_names = set()
        param_details:list[tuple] = []
        for key, param_value in params.items():
            spider_name, param_name = cls.split_param_name(key)
            spider_names.add(spider_name)
            if param_name != "NONE":
                param_details.append((spider_name, param_name, param_value))
        spiders = await SpiderAsset.filter(spider_name__in=list(spider_names))
        for spider_name, param_name, param_value in param_details:
            for spider in spiders:
                if spider.spider_name == spider_name:
                    spider_param = await SpiderParameter.get(
                        spider_id=spider, 
                        param_name=param_name
                    )
                    await ParameterValue.create(
                        campaign_id=campaign, 
                        parameter_id=spider_param,
                        value=param_value 
                    )
        await campaign.spiders.add(*spiders)
        return campaign


    @staticmethod
    def split_param_name(s:str) -> tuple[str, str]:
        """<Input> name attribute is:         
        "SpiderAsset.spider_name--SpiderParameter.param_name"
        """
        return tuple(s.split('--'))



# class SpiderConfiguration(Model):
#     campaign_id = fields.ForeignKeyField("models.Campaign", related_name="spider_config", on_delete=fields.CASCADE)



class ParameterValue(Model):
    """These are SpiderParameter values that are specific to a particular campaign"""
    campaign_id = fields.ForeignKeyField("models.Campaign", related_name="param_values", on_delete=fields.CASCADE)
    # config_id = fields.ForeignKeyField("models.SpiderConfiguration", related_name="param_values", on_delete=fields.CASCADE)
    parameter_id = fields.ForeignKeyField("models.SpiderParameter", related_name="param_values", on_delete=fields.CASCADE)
    value = fields.CharField(max_length=255)

    def param_value_details(self) -> dict:
        return instance_to_dict(self)



class ScrapeJob(Model):

    campaign_id     = fields.ForeignKeyField("models.Campaign", related_name="scrape_jobs", null=True, on_delete=fields.SET_NULL)
    # spiders         = fields.ManyToManyField("models.SpiderAsset", related_name="scrape_jobs")
    is_error        = fields.BooleanField(default=False)
    tables          = fields.ManyToManyField("models.ScrapeModuleTable", related_name="scrape_jobs")
    date_scraped    = fields.DatetimeField(auto_now_add=True)


    async def module_dir_path(self) -> Path:
        """Returns the Path object for where the campaign module's 
        scraped data will be saved to.
        """
        if self.campaign_id:
            campaign:Campaign = await self.campaign_id
            path = f"{CAMPAIGN_MODULES_DIR}/{campaign.campaign_name.lower()}"
        else:
            path = SOLO_SCRAPED_DATA_DIR

        return Path(path)


    async def module_scraped_data_path(self) -> Path:
        return await self.module_dir_path()# / Path('scraped_data') 



    async def scraped_tables(self) -> list[ScrapeModuleTable]:
        """Returns the tables containing data scraped by this scrape job."""
        return await self.tables.all()


    async def scraped_data(self, scrape_model_subclasses:list[Model], remove_job_id:bool=False) -> dict[str, list[Model]]:
        """Retrieve all the scraped data, across multiple tables, 
        that hold this job's id.
        """
        d = {}
        module_tables = await self.scraped_tables()
        module_table_names = set([table.table_name for table in module_tables])
        for cls in scrape_model_subclasses:
            if cls.__name__ in module_table_names:
                table_values = await cls.filter(scrape_job_id=self.id).values()
                if remove_job_id:
                    for row_dict in table_values:
                        # row_dict.pop('id')
                        row_dict.pop('scrape_job_id_id')
                d[cls.__name__] = table_values
                
        return d


    def count_records(self, scraped_data:dict[str, list[Model]]) -> int:
        """Count up all the records this job scraped."""
        records = 0
        for _, value in scraped_data.items():
            records += len(value)
        return records


    async def add_tables_to_scrape_job(self, registry_scrape_tables:list[ScrapeModuleTable]):
        """Adds the tables from the campaign registry's tables set to
        the scrape job's manytomany tables field.
        Creates the table if none exists.
        """            
        await self.tables.add(*registry_scrape_tables)


    async def get_campaign_dir(self) -> Path:
        """Gets the Campaign directory Path object."""
        campaign:Campaign = await self.campaign_id
        return campaign.campaign_dir()


# class ScrapeSchedule(Model):

#     campaign_id = fields.OneToOneField("models.Campaign", related_name="scape_schedule", on_delete=fields.CASCADE)
#     frequency   = fields.CharEnumField(FrequenciesEnum)
#     day_of_week = fields.CharEnumField(DaysEnum)
#     time_of_day = fields.TimeField()


