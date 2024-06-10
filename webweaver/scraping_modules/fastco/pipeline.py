from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.fastco.validation import FastcoSchema


class FastcoPipeline(Pipeline):

    schema = FastcoSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
