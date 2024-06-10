from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.ganjaexpress.validation import GanjaExpressSchema


class GanjaExpressPipeline(Pipeline):

	schema = GanjaExpressSchema

	async def save_data(self):
	# Add your pipeline logic here
		pass
