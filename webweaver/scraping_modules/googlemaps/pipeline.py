import logging
from tortoise.transactions import in_transaction

from webweaver.scraping_modules.googlemaps.validation import GoogleMapsSchema
from webweaver.scraping_modules.googlemaps.models import GoogleMapsCompany, GoogleMapsReview
from webweaver.webscraping.pipelines.pipeline_base import Pipeline 


logger = logging.getLogger("scraping")


class GoogleMapsPipeline(Pipeline):

    schema = GoogleMapsSchema

    async def save_data(self):

        async with in_transaction():
            reviews = []
            for data in self.batch_data_to_save:
                company_instance = await GoogleMapsCompany.create(**data.company.model_dump())
                review = data.review.model_dump()                
                review['company'] = company_instance
                reviews.append(GoogleMapsReview(**review))

            await GoogleMapsReview.bulk_create(reviews)

        return
    

