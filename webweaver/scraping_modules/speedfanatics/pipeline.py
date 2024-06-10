from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.speedfanatics.validation import SpeedFanaticsSchema


class SpeedFanaticsPipeline(Pipeline):

    schema = SpeedFanaticsSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
