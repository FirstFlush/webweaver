from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.yelp.validation import YelpSchema


class YelpPipeline(Pipeline):

	schema = YelpSchema

	async def save_data(self):
	# Add your pipeline logic here
		pass
