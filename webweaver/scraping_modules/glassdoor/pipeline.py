from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.glassdoor.validation import GlassDoorSchema


class GlassDoorPipeline(Pipeline):

	schema = GlassDoorSchema

	async def save_data(self):
	# Add your pipeline logic here
		pass
