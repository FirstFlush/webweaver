from enum import Enum
from tortoise import fields

from webweaver.webscraping.models import ScrapeModel


class BudRatingEnum(Enum):
    AAAAA = "AAAAA"
    AAAA = "AAAA"
    AAA = "AAA"
    AA = "AA"
    A_PLUS = "A+"
    A = "A"

class BcBudSupplyCategory(ScrapeModel):
    category_name = fields.CharField(max_length=255, unique=True)


class BcbudSupplySubCategory(ScrapeModel):
    category_name = fields.CharField(max_length=255, unique=True)



class BcBudSupplyProduct(ScrapeModel):

    product_name    = fields.CharField(max_length=255)
    source = fields.CharField(max_length=255)
    category        = fields.ForeignKeyField('models.BcBudSupplyCategory', related_name='products', on_delete=fields.CASCADE)


class BcBudSupplyBudRating(ScrapeModel):

    product     = fields.ForeignKeyField('models.BcBudSupplyProduct', related_name='ratings', on_delete=fields.CASCADE)
    rating      = fields.CharEnumField(BudRatingEnum)
    date        = fields.DatetimeField(auto_now_add=True)



class BcBudSupplyPrice(ScrapeModel):

    product     = fields.ForeignKeyField('models.BcBudSupplyProduct', related_name='prices', on_delete=fields.CASCADE)
    price       = fields.DecimalField(decimal_places=2, max_digits=15)
    is_sale     = fields.BooleanField(default=False)
    date        = fields.DatetimeField(auto_now_add=True)



class BcBudSupplyVariationType(ScrapeModel):
    """Types of variations include but not limited to:
        weight, color, size
    """
    type_name = fields.CharField(max_length=255)



class BcBudSupplyProductVariation(ScrapeModel):

    product         = fields.ForeignKeyField('models.BcBudSupplyProduct', related_name='prices', on_delete=fields.CASCADE)
    price           = fields.ForeignKeyField('models.BcBudSupplyPrice', related_name='variations', null=True) 
    variation_type  = fields.ForeignKeyField('models.BcBudVariationType', related_name='variations')



class BcBudSupplyBundle(ScrapeModel):
    title = fields.CharField(max_length=255)
    price = fields.DecimalField(decimal_places=2, max_digits=15)


