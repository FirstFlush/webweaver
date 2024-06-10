import logging
from tortoise import fields, Model
from typing import TYPE_CHECKING
from webweaver.project.handler_map import PROJECT_HANDLER_MAP
from webweaver.project.project_base import ProjectHandler

if TYPE_CHECKING:
    from webscraping.spiders.models import SpiderAsset


logger = logging.getLogger('scraping')


class Project(Model):

    project_name    = fields.CharField(max_length=255)
    description     = fields.TextField()
    date_created    = fields.DatetimeField(auto_now_add=True)


    async def spiders(self) -> list["SpiderAsset"]:
        """Gets a list of SpiderAsset objects used in the project, 
        as found in each campaign.
        """
        spiders = []
        for campaign in await self.campaigns.all():
            campaign_spiders = await campaign.spiders.all()
            spiders.extend(campaign_spiders)
        return spiders
    

    def get_handler(self) -> ProjectHandler:
        try:
            return PROJECT_HANDLER_MAP[self.id]
        except KeyError as e:
            logger.error(f"Project #{self.id} ({self.project_name}) has no handler!")
            raise