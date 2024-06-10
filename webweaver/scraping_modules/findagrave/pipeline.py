from webweaver.webscraping.pipelines.pipeline_base import Pipeline
import logging


logger = logging.getLogger("scraping")


class FindAGravePipeline(Pipeline):


    async def process_data(self):
        
        print(self.batch_data)

