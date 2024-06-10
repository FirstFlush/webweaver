import asyncio
from tortoise import Tortoise
from tortoise.transactions import in_transaction
from webweaver.config import all_models, POSTGRES_DB

from webweaver.modules.project_modules.speed_fanatics.models import (
    Category, 
    SubCategory, 
    Product,
    WheelAttribute,
    TireAttribute,
)
from webweaver.modules.project_modules.speed_fanatics.categorization.vehicle_handler import VehicleHandler
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum,
    SubCategoryEnum
)
# from webweaver.modules.project_modules.speed_fanatics.speed_regex import SpeedRegex


async def main():

    await Tortoise.init(db_url=POSTGRES_DB, modules={'models': all_models})

    product_names = [product.product_name for product in await Product.all()]

    handler = VehicleHandler(product_names)




if __name__ == '__main__':
    asyncio.run(main())