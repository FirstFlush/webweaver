from tortoise import fields

from webweaver.webscraping.models import ScrapeModel
from webweaver.common.fields import EmailField


class EventsEyeIndustry(ScrapeModel):
    industry_name = fields.CharField(max_length=255, unique=True)


class EventsEyeOrganizer(ScrapeModel):
    organizer_name  = fields.CharField(max_length=255)
    website         = fields.CharField(max_length=2048, null=True)
    phone           = fields.CharField(max_length=255, null=True)
    email           = EmailField(max_length=255, null=True)


class EventsEyeVenue(ScrapeModel):
    venue_name      = fields.CharField(max_length=255)
    city            = fields.CharField(max_length=255, null=True)
    state           = fields.CharField(max_length=64, null=True)


class EventsEyeTradeShow(ScrapeModel):
    organizers      = fields.ManyToManyField('models.EventsEyeOrganizer', related_name='trade_shows')
    venue           = fields.ForeignKeyField('models.EventsEyeVenue', related_name='trade_shows', on_delete=fields.CASCADE, null=True)
    industries      = fields.ManyToManyField('models.EventsEyeIndustry', related_name='trade_shows')
    event_name      = fields.CharField(max_length=255)
    description     = fields.TextField()
    audience        = fields.CharField(max_length=255, default="Public", null=True)
    cycle           = fields.CharField(max_length=255)
    website         = fields.CharField(max_length=2048, null=True)
    email           = EmailField(max_length=255, null=True)
    country         = fields.CharField(max_length=255)
    date_uncertain  = fields.BooleanField(default=False)
    date            = fields.DateField()
    duration_days   = fields.SmallIntField()

    class Meta:
        unique_together = ('event_name', 'email', 'date')


