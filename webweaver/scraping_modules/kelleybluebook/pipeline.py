from tortoise.transactions import in_transaction

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.kelleybluebook.validation import KelleyBlueBookSchema
from webweaver.modules.project_modules.speed_fanatics.models import VehicleMake, VehicleModel


class KelleyBlueBookPipeline(Pipeline):

    schema = KelleyBlueBookSchema

    async def save_data(self):

        data_to_save:KelleyBlueBookSchema = self.batch_data_to_save[0]
        
        async with in_transaction():
            vehicle_make, _ = await VehicleMake.get_or_create(vehicle_make=data_to_save.vehicle_make)
            await VehicleModel.get_or_create(vehicle_make=vehicle_make, vehicle_model=data_to_save.vehicle_model)