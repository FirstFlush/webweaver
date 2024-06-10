from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.soulpp.validation import SoulPPSchema


class SoulPPPipeline(Pipeline):

    schema = SoulPPSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
