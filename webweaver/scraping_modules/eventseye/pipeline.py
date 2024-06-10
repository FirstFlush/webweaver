from tortoise.transactions import in_transaction
from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.scraping_modules.eventseye.models import (
    EventsEyeIndustry,
    EventsEyeOrganizer,
    EventsEyeTradeShow,
    EventsEyeVenue
)
from webweaver.scraping_modules.eventseye.validation import EventsEyeSchema


class EventsEyePipeline(Pipeline):

    schema = EventsEyeSchema

    async def save_data(self):

        data_to_save:EventsEyeSchema = self.batch_data_to_save[0]

        async with in_transaction():
            industry_instances = []
            organizer_instances = []
            for industry in data_to_save.industries:
                industry_instance = await EventsEyeIndustry.get_or_create(**industry.model_dump())
                industry_instances.append(industry_instance[0])

            for organizer in data_to_save.organizers:
                organizer_instance = await EventsEyeOrganizer.get_or_create(**organizer.model_dump())
                organizer_instances.append(organizer_instance[0])

            if data_to_save.venue:
                venue_tuple = await EventsEyeVenue.get_or_create(**data_to_save.venue.model_dump())
                venue = venue_tuple[0]
            else:
                venue = None

            event = await EventsEyeTradeShow.create(venue=venue, **data_to_save.event.model_dump())
            await event.organizers.add(*organizer_instances)
            await event.industries.add(*industry_instances)
            await event.save()
            print('='*80)
            print(f">> Saved event id#: {event.id}")
            print()