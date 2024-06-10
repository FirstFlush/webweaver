from webscraping.pipelines.pipeline_base import Pipeline
from webscraping.modules.test.schema import TestSchema


class TestPipeline(Pipeline):

	schema = TestSchema

	async def save_data(self):
	# Add your pipeline logic here
		pass
