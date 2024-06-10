from pydantic import BaseModel, validator

from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner

from modules.project_modules.speed_fanatics.models import Product, ProductImageUrl
from .spider import ImageData

class SpeedFanaticsImageSchema(BaseModel):

    image_data: ImageData
    # product: Product
    # product_image_url: ProductImageUrl
    # image: bytes

    class Config:
        arbitrary_types_allowed = True
