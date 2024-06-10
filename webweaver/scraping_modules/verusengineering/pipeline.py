from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.verusengineering.validation import VerusEngineeringSchema


class VerusEngineeringPipeline(Pipeline):

    schema = VerusEngineeringSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
