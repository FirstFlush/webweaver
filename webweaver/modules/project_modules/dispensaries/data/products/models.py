from tortoise import fields, Model
from tortoise.functions import Max
from tortoise.transactions import in_transaction

from webweaver.common.enums import BudRatingEnum, DataTypeEnum
from webweaver.common.fields import EmailField
from webweaver.webscraping.models import ScrapeModel
# from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_mapping import VariationEnum
from webweaver.modules.project_modules.dispensaries.dispensary_enum import DispensaryEnum


class PriceModel(ScrapeModel):
    """The current price (or prices) of a Product/Bundle is determined
    by grabbing all prices at whatever the most recent 'date_last_seen' value is.
    By grabbing only the price or prices with the most recent date_last_seen value, 
    we are guaranteeing we are only the variation prices for variations that are
    still available.
    
    ProductPrice & BundlePrice both share some functionality, particularly
    related to querying prices of the most recently scraped date. This class
    is to provide shared functionality for both ProductPrice & BundlePrice.
    """
    class Meta:
        abstract = True


class CannabisBrand(ScrapeModel):
    brand_name      = fields.CharField(max_length=255, unique=True)
    date_scraped    = fields.DatetimeField(auto_now_add=True)


class Dispensary(Model):
    spider_asset    = fields.OneToOneField('models.SpiderAsset', null=True, related_name='dispensary', on_delete=fields.SET_NULL)
    dispensary_enum = fields.CharEnumField(DispensaryEnum, index=True)
    brands          = fields.ManyToManyField('models.CannabisBrand', related_name='dispensaries')
    email           = EmailField(max_length=255, null=True)
    is_active       = fields.BooleanField(default=True)
    date_created    = fields.DatetimeField(auto_now_add=True)
    # seo_ranking(s)?




class Category(Model):
    category_name   = fields.CharField(max_length=255, unique=True)
    is_active       = fields.BooleanField(default=True)

class SubCategory(Model):
    subcategory_name    = fields.CharField(max_length=255, unique=True)
    is_active           = fields.BooleanField(default=True)


class VariationType(Model):
    """Types of variations include but not limited to:
        weight, color, size, flavour
    """
    type_name   = fields.CharField(max_length=255)
    data_type   = fields.CharEnumField(DataTypeEnum)
    datetime    = fields.DatetimeField(auto_now_add=True)


class Variation(Model):

    variation_type  = fields.ForeignKeyField('models.VariationType', related_name='variations', on_delete=fields.CASCADE)
    variation_num   = fields.FloatField(null=True)
    variation_str   = fields.CharField(max_length=255, null=True)



class Product(ScrapeModel):

    dispensary      = fields.ForeignKeyField('models.Dispensary', related_name='products', on_delete=fields.CASCADE)
    category        = fields.ForeignKeyField('models.Category', related_name='products', on_delete=fields.CASCADE)
    subcategory     = fields.ForeignKeyField('models.SubCategory', related_name='products', on_delete=fields.CASCADE)
    variations      = fields.ManyToManyField('models.Variation', related_name='products')
    product_name    = fields.CharField(max_length=255)
    date_last_seen  = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product_name', 'dispensary'),)


    async def get_variations(self) -> list[Variation]:
        return await self.variations.all()


class ProductDescription(ScrapeModel):
    """This table is so I can create a collection of 
    product descriptions to train my NER and NLP models. 
    Then I can start picking out flavors, strain types, effects, etc.
    """
    product_name    = fields.CharField(max_length=255)
    text            = fields.TextField()
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product_name', 'text'),)



class BudRating(ScrapeModel):

    product     = fields.ForeignKeyField('models.Product', related_name='ratings', on_delete=fields.CASCADE)
    rating      = fields.CharEnumField(BudRatingEnum)
    datetime    = fields.DatetimeField(auto_now_add=True)


class ProductPrice(PriceModel):
    product         = fields.ForeignKeyField('models.Product', related_name='prices', on_delete=fields.CASCADE)
    variation       = fields.ForeignKeyField('models.Variation', related_name='prices', null=True)
    price           = fields.DecimalField(decimal_places=2, max_digits=15)
    is_sale         = fields.BooleanField(default=False)
    date_last_seen  = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'price', 'variation', 'is_sale')

    async def get_current_prices(self) -> list[dict]:
        query = """
            SELECT prod.*, price.*
            FROM product prod
            INNER JOIN (
                SELECT product_id, MAX(date_last_seen) as max_date
                FROM productprice
                GROUP BY product_id
            ) pricemax ON prod.id = pricemax.product_id
            INNER JOIN productprice price ON price.product_id = prod.id AND price.date_last_seen = pricemax.max_date;
        """

        async with in_transaction() as connection:
            results = await connection.execute_query_dict(query)
            return results




class Bundle(ScrapeModel):
    dispensary      = fields.ForeignKeyField('models.Dispensary', related_name='bundles', on_delete=fields.CASCADE)
    products        = fields.ManyToManyField('models.Product')
    category        = fields.ForeignKeyField('models.Category', related_name='bundles', on_delete=fields.CASCADE)
    subcategory     = fields.ForeignKeyField('models.SubCategory', related_name='bundles', on_delete=fields.CASCADE)
    bundle_name     = fields.CharField(max_length=255)
    # price           = fields.DecimalField(decimal_places=2, max_digits=15, null=True)
    # prince_range    = fields.DecimalField(decimal_places=2, max_digits=15, null=True)
    datetime        = fields.DatetimeField(auto_now_add=True)


class BundlePrice(PriceModel):
    bundle          = fields.ForeignKeyField('models.Bundle', related_name='prices', on_delete=fields.CASCADE)
    price           = fields.DecimalField(decimal_places=2, max_digits=15)
    is_sale         = fields.BooleanField(default=False)
    date_last_seen  = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)


    async def get_current_prices(self) -> list[dict]:
        query = """
            SELECT bundle.*, price.*
            FROM product bundle
            INNER JOIN (
                SELECT bundle_id, MAX(date_last_seen) as max_date
                FROM bundleprice
                GROUP BY bundle_id
            ) pricemax ON bundle.id = pricemax.bundle_id
            INNER JOIN bundleprice price ON price.bundle_id = bundle.id AND price.date_last_seen = pricemax.max_date;
        """

        async with in_transaction() as connection:
            results = await connection.execute_query_dict(query)
            return results