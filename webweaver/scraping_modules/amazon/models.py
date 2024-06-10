from tortoise import fields
from webweaver.webscraping.models import ScrapeModel


class AmazonProduct(ScrapeModel):

    product_name = fields.CharField(max_length=255)
    list_price = fields.DecimalField(max_digits=16, decimal_places=2)
    review_score = fields.FloatField(null=True)
    review_count = fields.IntField(null=True)
    bought_past_month = fields.IntField(null=True)