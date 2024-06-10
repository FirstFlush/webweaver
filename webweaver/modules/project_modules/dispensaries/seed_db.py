# import asyncio
# from tortoise import Tortoise
# from tortoise.models import Model
# from typing import Any

# from webweaver.config import all_models, POSTGRES_DB
# from webweaver.modules.project_modules.dispensaries.data.products.models import (
#     VariationType,
#     Category,
#     SubCategory
# )


# variation_types = [
#     {'type_name':'weight', 'data_type':'float'},
#     {'type_name':'size', 'data_type':'string'},
#     {'type_name':'flavor', 'data_type':'string'},
#     {'type_name':'color', 'data_type':'string'},
# ]

# categories = [
#     {'category_name': 'flower'},
#     {'category_name': 'concentrates'},
#     {'category_name': 'edibles'},
#     {'category_name': 'cbd'},
#     {'category_name': 'vapes'},
#     # {'category_name': },
# ]

# subcategories = [
#     #flower
#     {'subcategory_name': 'indica'},
#     {'subcategory_name': 'sativa'},
#     {'subcategory_name': 'hybrid'},
#     {'subcategory_name': 'preroll'},
#     #concentrates
#     {'subcategory_name': 'diamonds'},
#     {'subcategory_name': 'hash'},
#     {'subcategory_name': 'shatter'},
#     {'subcategory_name': 'live resin'},
#     {'subcategory_name': 'rosin'},
#     {'subcategory_name': 'keef'},
#     {'subcategory_name': 'budder'},
#     # {'subcategory_name': ''},
#     #edibles
#     {'subcategory_name': 'candy'},
#     {'subcategory_name': 'chocolate'},
#     {'subcategory_name': 'gummies'},
#     {'subcategory_name': 'beverages'},
#     {'subcategory_name': 'tinctures'},
#     {'subcategory_name': 'oil'},
#     {'subcategory_name': 'baking'},
#     # {'subcategory_name': ''},
#     #cbd
#     # {'subcategory_name': 'cbd edibles'},
#     # {'subcategory_name': 'cbd oils'},
#     # {'subcategory_name': 'cbd powder'},
#     #vapes
#     {'subcategory_name': 'batteries'},
#     {'subcategory_name': 'catridges'},

# ]



# class DBSeeder:

#     async def _connect(self):
#         await Tortoise.init(db_url=POSTGRES_DB, modules={'models': all_models})
#         await Tortoise.generate_schemas()

#     async def seed_db(self):
#         await self._connect()
#         await self._seed_db_table(table=VariationType, seeds=variation_types)
#         await self._seed_db_table(table=Category, seeds=categories)
#         await self._seed_db_table(table=SubCategory, seeds=subcategories)

#     async def _seed_db_table(self, table:Model, seeds:list[dict[str, Any]]):
#         for i, _ in enumerate(seeds):
#             await table.get_or_create(**seeds[i])


# if __name__ == '__main__':
#     db_seeder = DBSeeder()
#     asyncio.run(db_seeder.seed_db())


