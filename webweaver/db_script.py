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
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
# from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
#     CategoryEnum,
#     SubCategoryEnum
# )
from webweaver.modules.project_modules.speed_fanatics.speed_regex import SpeedRegex

# This file exists in case I need to do any quick-n-dirty database operations
# through Tortoise-ORM instead of through Azure Data Studio.
# ---------------------------------------------------------------------------
# Always use in_transaction() for every script!




category_mapping = {
    'autobody' : 'Autobody',
    'brakes' : 'Brakes',
    'exhaust' : 'Exhaust',
    'intake' : 'Intake',
    'racewear' : 'Racewear',
    'suspension' : 'Suspension',
    'tires' : 'Tires',
    'tire_acessories' : 'Tire Accessories',
    'wheels' : 'Wheels',
    'wheel_accessories' : 'Wheel Accessories',
    'unknown' : 'Unknown',
}


async def main():

    await Tortoise.init(db_url=POSTGRES_DB, modules={'models': all_models})
    # await Tortoise.generate_schemas()
    # ---------------------------------------------------------------------

    async with in_transaction():

        for old_name, new_name in category_mapping.items():
            await Category.filter(category_name=old_name).update(category_name=new_name)


        # categories = await Category.all()
        # for category in categories:

        #     new_category_name = category.category_name = category_mapping[category.category_name.value]
            
            
        #     await category.save()

if __name__ == '__main__':
    asyncio.run(main())







# class FuckThis:

#     #Autobody
#     BODY_KITS = 'Body Kits'
#     SPOILERS = 'Spoilers'
#     DIFFUSERS = 'Diffusers'
#     AUTOBODY_MISC = 'Autobody Misc'
#     #Brakes
#     BRAKE_BUNDLES = 'Brake Bundles' # pads, lines, fluid, discs that work with OEM calipers
#     BRAKE_CALIPERS = 'Brake Calipers'
#     BRAKE_DISCS = 'Brake Discs'
#     BRAKE_FLUIDS = 'Brake Fluids'
#     BRAKE_KITS = 'Brake Kits'
#     BRAKE_LINES = 'Brake Lines'
#     BRAKE_PADS = 'Brake Pads'
#     MASTER_CYLINDERS = 'Master Cylinders'
#     #Exhaust
#     EXHAUST_SYSTEMS = 'Exhaust Systems'
#     #Intake
#     AIR_FILTERS = 'Air Filters'
#     #Racewear
#     SUITS = 'Suits'
#     BOOTS = 'Boots'
#     GLOVES = 'Gloves'
#     HELMETS = 'Helmets'
#     CLOTHING = 'Clothing'
#     #Suspension
#     BAR_BUSHINGS = 'Bar Bushings'
#     SHOCK_ABSORBERS = 'Shock Absorbers'
#     SPRINGS = 'Springs'
#     STRUTS = 'Struts'
#     SWAY_BARS = 'Sway Bars'
#     #Tires
#     TIRES_SUMMER = 'Summer Tires' 
#     TIRES_WINTER = 'Winter Tires'
#     TIRES_ALL_SEASON = 'All-Season Tires'
#     TIRES_ALL_WEATHER = 'All-Weather Tires'
#     TIRES_ALL_TERRAIN = 'All-Terrain Tires'
#     TIRES_MUD = 'Mud Tires'
#     #Tire Accessories
#     TIRES_MISC = 'Tire Misc'
#     TIRES_STUDS = 'Tire Studs'
#     TIRES_VALVES = 'Valves'
#     TPMS = 'TPMS'
#     #Wheels
#     WHEELS_AUTOMOTIVE = 'Wheels - Automotive'
#     WHEELS_UTV_ATV = 'Wheels - UTV/ATV'
#     #Wheel Accessories
#     WHEEL_HUB_RINGS = 'Hub Rings'
#     WHEEL_SPACERS = 'Wheel Spacers'
#     WHEEL_ADAPTERS = 'Wheel Adapters'
#     WHEEL_MISC = 'Wheel Misc'
#     WHEEL_NUTS_BOLTS = 'Nuts & Bolts'
#     WHEEL_CAPS = 'Wheel Caps'
#     WHEEL_RIVETS = 'Wheel Rivets'
#     #Unknown
#     UNKNOWN = 'Unknown'












































    # wheel_attributes = await WheelAttribute.all()

    # for wheel_attribute in wheel_attributes:
    #     if not wheel_attribute.load_rating:
    #         continue

    #     try:
    #         load_rating = float(wheel_attribute.load_rating.replace('kg',''))
    #     except ValueError:
    #         load_indices = SpeedRegex.extract_numbers.findall(wheel_attribute.load_rating)
    #         if len(load_indices) != 2:
    #             print(f"\tInvalid load_rating string: {wheel_attribute.load_rating}")
    #         load_rating = min([float(load_index) for load_index in load_indices])

    #     wheel_attribute.load_rating_temp = load_rating
    #     await wheel_attribute.save()
