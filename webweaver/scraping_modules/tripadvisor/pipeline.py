from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.tripadvisor.validation import TripAdvisorSchema


class TripAdvisorPipeline(Pipeline):

    schema = TripAdvisorSchema

    async def save_data(self):
    # Add your pipeline logic here
        pass
