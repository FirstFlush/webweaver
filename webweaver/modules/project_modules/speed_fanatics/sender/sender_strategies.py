from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import logging
from typing import Any, Union

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


logger = logging.getLogger("sending")


class SenderStrategy:

    label:Enum = None
    model:Model = None
    values:tuple[str] = None
    prefetch:tuple[str] = None
    rows:list[dict[str, Any]] = []


    @classmethod
    async def select_strategy(cls) -> "SenderStrategy":
        """Factory method for creating a strategy and populating its rows"""        
        strategy = cls()
        strategy.rows = await strategy.query()
        await strategy.hook()
        for row in strategy.rows:
            cls._coerce_types(row)
        return strategy


    @staticmethod
    def _coerce_types(row:dict[str, Any]):
        for k, v in row.items():
            if isinstance(v, (datetime, date)):
                row[k] = v.isoformat()
            elif isinstance(v, Enum):
                row[k] = v.value
            elif isinstance(v, Decimal):
                row[k] = float(v)


        # if isinstance(value, (datetime, date)):
        #     processed_row[key] = value.isoformat()
        # elif isinstance(value, Enum):
        #     processed_row[key] = cls.enum_value(value)
        # elif isinstance(value, Decimal):
        #     processed_row[key] = cls.convert_decimal(value)
        # else:
        #     processed_row[key] = value

    async def hook(self):
        """Hook each strategy can implement for extra processing"""
        return


    async def query(self) -> list[dict[str, Any]]:
        """Right now it is all(). This could be changed to only grab records
        that have a 'date_scraped' value of less than 1 month (for example)
        """
        if self.prefetch:
            return await self.model.all().prefetch_related(*self.prefetch).values(*self.values)
        else:
            return await self.model.all().values(*self.values)




class SupplierSendStrategy(SenderStrategy):

    label = TableLabelEnum.SUPPLIER
    model = Supplier
    values = (
        'supplier_name',
        'is_active',
        'country',
    )

class BrandSendStrategy(SenderStrategy):

    label = TableLabelEnum.BRAND
    model = Brand
    values = (
        'brand_name',
    )


class CategorySendStrategy(SenderStrategy):

    label = TableLabelEnum.CATEGORY
    model = Category
    values = (
        'category_name',
        'is_active',
    )


class SubCategorySendStrategy(SenderStrategy):

    label = TableLabelEnum.SUBCATEGORY
    model = SubCategory
    values = (
        'subcategory_name',
        'category__category_name',
        'is_active',
    )

class ProductSendStrategy(SenderStrategy):

    label = TableLabelEnum.PRODUCT
    model = Product
    values = (
        'category__category_name',
        'subcategory__subcategory_name',
        'brand__brand_name',
        'supplier__supplier_name',
        'product_name',
        'product_code',
        'description',
        'description_long',
        'is_active',
        'is_sale',
        'is_special_order',
    )

    async def hook(self):
        await self.product_price()

    async def product_price(self):
        """The store has no need of a dedicated Price table. This method will
        merge product price data into the product table.
        """
        for row in self.rows:
            product = await Product.get(
                product_name=row['product_name'],
                supplier__supplier_name=row['supplier__supplier_name'],
            )
            msrp = await product.get_msrp()
            row['price'] = float(msrp)



class VariationTypeSendStrategy(SenderStrategy):

    label = TableLabelEnum.VARIATION_TYPE
    model = VariationType
    values = (
        'data_type',
        'variation_type_name',
        'is_required',
    )


class ProductVariationSendStrategy(SenderStrategy):

    label = TableLabelEnum.PRODUCT_VARIATION
    model = ProductVariation
    values = (
        'product__product_name',
        'product__supplier__supplier_name',
        'variation_type__variation_type_name',
        'value',
        'price_modifier',
    )
    prefetch = (
        'required_variations',
    )

    async def hook(self):
        for row in self.rows:
            await self.get_required_variations(row)


    async def get_required_variations(self, row:dict[str, Any]):

        var = await ProductVariation.get(
            product__product_name=row['product__product_name'],
            variation_type__variation_type_name=row['variation_type__variation_type_name'],
            value=row['value'],
        ).prefetch_related(*self.prefetch)
        if var.required_variations:
            for required_var in var.required_variations:
                ...
                # NOTE: 
                # -build required_var dict
                # -pass dict to list of dicts
                # -make list of dicts the value of row['required_variations'] 
        

class TireAttributeSendStrategy(SenderStrategy):

    label = TableLabelEnum.TIRE_ATTRIBUTE
    model = TireAttribute
    values = (
        'product__product_name',
        'product__supplier__supplier_name',
        'width',
        'aspect_ratio',
        'wheel_diameter',
        'load_index',
        'load_index_dual',
        'speed_rating',
        'load_description',
        'utqg',
        'overall_diameter',
        'studdable',
        'service_type',
    )



class WheelAttributeSendStrategy(SenderStrategy):

    label = TableLabelEnum.WHEEL_ATTRIBUTE
    model = WheelAttribute
    values = (
        'product__product_name',
        'product__supplier__supplier_name',
        'diameter',
        'width',
        'centerbore',
        'bolt_pattern',
        'finish',
        'load_rating',
        'weight',
        'backspacing',
        'offset',
    )

class CostSendStrategy(SenderStrategy):

    label = TableLabelEnum.COST
    model = Cost
    values = (
        'product__product_name',
        'product__supplier__supplier_name',
        'cost',
    )


class ProductImageSendStrategy(SenderStrategy):

    label = TableLabelEnum.PRODUCT_IMAGE
    model = ProductImage
    values = (
        'product__product_name',
        'product__supplier__supplier_name',
        # 'is_primary',

    )
