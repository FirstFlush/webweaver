from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.greensociety.validation import GreenSocietySchema
from tortoise.transactions import in_transaction


class GreenSocietyPipeline(Pipeline):

    schema = GreenSocietySchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
