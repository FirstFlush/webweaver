from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import logging
from typing import Any
from tortoise.models import Model
from webweaver.modules.project_modules.speed_fanatics.speed_enums import TableLabelEnum
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier,
    Category, 
    SubCategory, 
    Product,
    WheelAttribute,
    TireAttribute,
    AddOn,
    ProductImage,
    Price,
    Cost,
    Brand,
    ProductVariation,
    VariationType,
)


logger = logging.getLogger("scraping")


class ModelHooks:
    """This class is in case we need some specialized behavior 
    for processing a particular table. These hook functions will
    be called from TableData's get_table_data() method.
    """

    @classmethod
    async def product_price(cls, table_data:"TableData"):
        """The store has no need of a dedicated Price table. This method will
        merge product price data into the product table.
        """
        for data_dict in table_data.data:
            product = await Product.get(id=data_dict['id'])
            msrp = await product.get_msrp()
            data_dict['price'] = float(msrp)




class SenderData:

    label = None
    model = None
    data = []


class SupplierSend(SenderData):

    label = TableLabelEnum.SUPPLIER
    model = Supplier


class BrandSend(SenderData):

    label = TableLabelEnum.BRAND
    model = Brand


class CategorySend(SenderData):

    label = TableLabelEnum.CATEGORY
    model = Category


class SubCategorySend(SenderData):

    label = TableLabelEnum.SUBCATEGORY
    model = SubCategory


class ProductSend(SenderData):

    label = TableLabelEnum.PRODUCT
    model = Product


class VariationTypeSend(SenderData):

    label = TableLabelEnum.VARIATION_TYPE
    model = VariationType


class ProductVariationSend(SenderData):

    label = TableLabelEnum.PRODUCT_VARIATION
    model = ProductVariation


class TireAttributeSend(SenderData):

    label = TableLabelEnum.TIRE_ATTRIBUTE
    model = TireAttribute


class WheelAttributeSend(SenderData):

    label = TableLabelEnum.WHEEL_ATTRIBUTE
    model = WheelAttribute


class CostSend(SenderData):

    label = TableLabelEnum.COST
    model = Cost


class ProductImageSend(SenderData):

    label = TableLabelEnum.PRODUCT_IMAGE
    model = ProductImage








class TableData:

    def __init__(self, label:TableLabelEnum, data:list[dict[str, Any]]):
        self.label = label
        self.data = data


    @classmethod
    async def get_table_data(cls, model:Model, label:TableLabelEnum, excluded_cols:set=None) -> dict[str, Any]:
        """Creates a TableData object and then prepares a serializable-dictionary to be sent to the store."""
        table_data = await cls.create_table_data(model=model, label=label, excluded_cols=excluded_cols)
        match label:
            case TableLabelEnum.PRODUCT:
                await ModelHooks.product_price(table_data=table_data)
            case _:
                pass
        
        return {
            'label': table_data.label.value,
            'data': table_data.data
        }


    @classmethod
    async def create_table_data(cls, model:Model, label:TableLabelEnum, excluded_cols:set=None) -> "TableData":
        """Factory method for creating table data object to transfer to the store."""
        data = await cls._preprocess(model=model, excluded_cols=excluded_cols)

        return cls(label, data)


    @classmethod
    def convert_decimal(self, num:Decimal) -> float:
        if isinstance(num, Decimal):
            return float(num)
        raise ValueError(f"parameter `num` value: {num}")


    @classmethod
    def enum_value(cls, enum:Enum) -> str:
        if isinstance(enum, Enum):
            return enum.value
        raise ValueError(f"parameter `enum` value: {enum}")


    @classmethod
    async def _preprocess(cls, model:Model, excluded_cols:set=None) -> list[dict[str, Any]]:
        """This method fetches the table rows and then removes the columns that are in the
        excluded_cols set and also converts any date/datetime objects to iso format.
        Returns a list of dicts, ready to be serialized.
        """
        _excluded_cols = {
            'scrape_job_id_id',
            'spider_asset',
            'spider_asset_id',
        }
        excluded_cols = _excluded_cols.union(excluded_cols) if excluded_cols else _excluded_cols
        rows =  await model.all().values()
        processed_rows = []
        for row_dict in rows:
            processed_row = {}
            for key, value in row_dict.items():
                if key not in excluded_cols:
                    if isinstance(value, (datetime, date)):
                        processed_row[key] = value.isoformat()
                    elif isinstance(value, Enum):
                        processed_row[key] = cls.enum_value(value)
                    elif isinstance(value, Decimal):
                        processed_row[key] = cls.convert_decimal(value)
                    else:
                        processed_row[key] = value
            processed_rows.append(processed_row)
        return processed_rows


























# from datetime import date, datetime
# from decimal import Decimal
# from enum import Enum
# import logging
# from typing import Any
# from tortoise.models import Model
# from webweaver.modules.project_modules.speed_fanatics.speed_enums import TableLabelEnum
# from webweaver.modules.project_modules.speed_fanatics.models import Product, Price


# logger = logging.getLogger("scraping")


# class ModelHooks:
#     """This class is in case we need some specialized behavior 
#     for processing a particular table. These hook functions will
#     be called from TableData's get_table_data() method.
#     """

#     @classmethod
#     async def product_price(cls, table_data:"TableData"):
#         """The store has no need of a dedicated Price table. This method will
#         merge product price data into the product table.
#         """
#         for data_dict in table_data.data:
#             product = await Product.get(id=data_dict['id'])
#             msrp = await product.get_msrp()
#             data_dict['price'] = float(msrp)


# class TableData:

#     def __init__(self, label:TableLabelEnum, data:list[dict[str, Any]]):
#         self.label = label
#         self.data = data


#     @classmethod
#     async def get_table_data(cls, model:Model, label:TableLabelEnum, excluded_cols:set=None) -> dict[str, Any]:
#         """Creates a TableData object and then prepares a serializable-dictionary to be sent to the store."""
#         table_data = await cls.create_table_data(model=model, label=label, excluded_cols=excluded_cols)
#         match label:
#             case TableLabelEnum.PRODUCT:
#                 await ModelHooks.product_price(table_data=table_data)
#             case _:
#                 pass
        
#         return {
#             'label': table_data.label.value,
#             'data': table_data.data
#         }


#     @classmethod
#     async def create_table_data(cls, model:Model, label:TableLabelEnum, excluded_cols:set=None) -> "TableData":
#         """Factory method for creating table data object to transfer to the store."""
#         data = await cls._preprocess(model=model, excluded_cols=excluded_cols)
#         print(data)
#         exit(0)
#         return cls(label, data)


#     @classmethod
#     def convert_decimal(self, num:Decimal) -> float:
#         if isinstance(num, Decimal):
#             return float(num)
#         raise ValueError(f"parameter `num` value: {num}")


#     @classmethod
#     def enum_value(cls, enum:Enum) -> str:
#         if isinstance(enum, Enum):
#             return enum.value
#         raise ValueError(f"parameter `enum` value: {enum}")


#     @classmethod
#     async def _preprocess(cls, model:Model, excluded_cols:set=None) -> list[dict[str, Any]]:
#         """This method fetches the table rows and then removes the columns that are in the
#         excluded_cols set and also converts any date/datetime objects to iso format.
#         Returns a list of dicts, ready to be serialized.
#         """
#         _excluded_cols = {
#             'scrape_job_id_id',
#             'spider_asset',
#             'spider_asset_id',
#         }
#         excluded_cols = _excluded_cols.union(excluded_cols) if excluded_cols else _excluded_cols
#         rows =  await model.all().values()
#         processed_rows = []
#         for row_dict in rows:
#             processed_row = {}
#             for key, value in row_dict.items():
#                 if key not in excluded_cols:
#                     if isinstance(value, (datetime, date)):
#                         processed_row[key] = value.isoformat()
#                     elif isinstance(value, Enum):
#                         processed_row[key] = cls.enum_value(value)
#                     elif isinstance(value, Decimal):
#                         processed_row[key] = cls.convert_decimal(value)
#                     else:
#                         processed_row[key] = value
#             processed_rows.append(processed_row)
#         return processed_rows

