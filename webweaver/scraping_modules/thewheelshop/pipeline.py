from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.thewheelshop.validation import TheWheelShopSchema


class TheWheelShopPipeline(Pipeline):

    schema = TheWheelShopSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
