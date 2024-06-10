import traceback

from tortoise.transactions import in_transaction
from tortoise.exceptions import TransactionManagementError, IntegrityError

from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.autoevolution.validation import AutoEvolutionSchema
from webweaver.modules.project_modules.speed_fanatics.models import VehicleMake, VehicleModel


class AutoEvolutionPipeline(Pipeline):

    schema = AutoEvolutionSchema

    async def save_data(self):
        data_to_save:AutoEvolutionSchema = self.batch_data_to_save[0]
        async with in_transaction():
            try:
                vehicle_make, _ = await VehicleMake.get_or_create(vehicle_make=data_to_save.vehicle_make)
                vehicle_model, _ = await VehicleModel.get_or_create(
                    vehicle_make=vehicle_make, 
                    vehicle_model=data_to_save.vehicle_model
                )
            except (TransactionManagementError, IntegrityError) as e:
                print(e.__class__.__name__, " : ", data_to_save.vehicle_make, " : ", data_to_save.vehicle_model)
                # print()
                # traceback.print_exc()
                # print()
                # exit(0)
            else:
                print(vehicle_model.vehicle_model, " => ", vehicle_make.vehicle_make)