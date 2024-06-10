from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.amazon.schema import AmazonSchema


class AmazonPipeline(Pipeline):

	schema = AmazonSchema

	async def save_data(self):
	# Add your pipeline logic here
		pass
