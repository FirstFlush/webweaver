import os
from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.speedfanaticsimage.validation import SpeedFanaticsImageSchema
from webweaver.modules.project_modules.speed_fanatics.models import ProductImage
from .validation import SpeedFanaticsImageSchema


class SpeedFanaticsImagePipeline(Pipeline):

    schema = SpeedFanaticsImageSchema

    async def save_data(self):

        self.data_to_save:SpeedFanaticsImageSchema
        file_name = None

        try:        
            async with in_transaction():
                file_name = ProductImage.create_file_name(
                    supplier_enum = self.data_to_save.image_data.product.supplier.supplier_name,
                    product_name = self.data_to_save.image_data.product.product_name,
                )

                image_instance = await ProductImage.create(
                    product = self.data_to_save.image_data.product,
                    file_name = file_name
                )
                image_instance.save_image_file(
                    binary_data = self.data_to_save.image_data.image,
                    file_name = file_name,
                )
                product_image_url = self.data_to_save.image_data.product_image_url
                product_image_url.image_scraped = True
                await product_image_url.save()

                print(f"[SAVED]\t{file_name}")
        except Exception as e:
            print(f"[Error]\t{e}")
            if file_name and os.path.exists(file_name):
                os.remove(file_name)
                print(f"Removed file: {file_name}")
