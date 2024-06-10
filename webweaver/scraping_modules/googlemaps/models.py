from tortoise import fields

from webweaver.webscraping.models import ScrapeModel
from webweaver.common.fields import URLField


class GoogleMapsCompany(ScrapeModel):
    company_name    = fields.CharField(max_length=255)
    address         = fields.CharField(max_length=255)
    phone           = fields.CharField(max_length=255, null=True)
    url             = URLField(max_length=2083, null=True) # URL max length in Chrome browser
    # country         = fields.ForeignKeyField("models.Country", on_delete=fields.CASCADE)


class GoogleMapsReview(ScrapeModel):
    company         = fields.ForeignKeyField('models.GoogleMapsCompany', related_name='reviews', on_delete=fields.CASCADE)
    # source_id       = fields.ForeignKeyField('models.ReviewSource', related_name='reviews', on_delete=fields.CASCADE)
    review_score    = fields.FloatField()
    review_count    = fields.IntField()
    # date_created    = fields.DatetimeField(auto_now_add=True)
