from tortoise.transactions import in_transaction
from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.modules.project_modules.dispensaries.weed_validation import WeedValidationSchema


class WeedPipeline(Pipeline):

    schema = WeedValidationSchema


    async def save_data(self):
        ...