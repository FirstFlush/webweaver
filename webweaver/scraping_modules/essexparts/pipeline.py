from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.essexparts.validation import EssexPartsSchema


class EssexPartsPipeline(Pipeline):

    schema = EssexPartsSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
