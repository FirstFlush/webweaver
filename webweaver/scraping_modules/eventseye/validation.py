from pydantic import (
    BaseModel, 
    EmailStr, 
    HttpUrl,
    validator,
    ValidationError, 
    validate_email
)
from datetime import datetime
from dateutil import parser
from typing import Optional, List

from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class IndustrySchema(BaseModel):
    industry_name: str


class OrganizerSchema(BaseModel):
    organizer_name: str
    phone: Optional[str]
    website: Optional[HttpUrl]
    email: Optional[EmailStr]

    @validator('email', pre=True)
    def fix_email(cls, value):
        #EventsEye has screwy emails that sometimes have spaces or \u200b aka "ZERO WIDTH SPACE chars"
        if value:
            return value.replace(" ", "").replace("\u200b", "").replace("\u00AD", "")
            # value = value.replace(" ", "").replace("\u200b", "")
            # return validate_email(value)[1]


class VenueSchema(BaseModel):
    venue_name: str
    city: Optional[str]
    state: Optional[str]


class EventSchema(BaseModel):
    event_name: str
    description: str
    cycle: str
    website: Optional[HttpUrl]
    email: Optional[EmailStr]
    country: str
    date_uncertain: bool = False
    date: datetime
    duration_days: Optional[int]

    @validator('email', pre=True)
    def fix_email(cls, value):
        #EventsEye has screwy emails that sometimes have spaces or \u200b aka "ZERO WIDTH SPACE chars"
        if value:
            return value.replace(" ", "").replace("\u200b", "").replace("\u00AD", "")
            # value = value.replace(" ", "").replace("\u200b", "")
            # return validate_email(value)[1]

    @validator('date', pre=True)
    def parse_date(cls, value:str, values, **kwargs):
        try:
            return PipelineCleaner.to_datetime(value, '%m/%d/%Y')
        except ValueError:
            default_datetime = datetime(year=1, month=1, day=1)
            if "(?)" in value:
                value = value.replace("(?)", "")
            try:
                parsed_date = parser.parse(value, default=default_datetime)
            except ValueError:
                print(value)
                raise ValidationError()
            else:
                values['date_uncertain'] = True
                return parsed_date

    @validator('duration_days', pre=True)
    def parse_duration(cls, value):
        """duration comes in many formats lol:
            -sometimes the element doesnt exist (means 1 day duration)
            -sometimes the element's text says '1 day'
            -sometimes the element's text is '(?)'. this should be None
        """
        if value:
            int_value = PipelineCleaner.to_int_or_none(value)
            if int_value:
                return int_value
            else:
                return None
        return 1 # single day duration if element does not exist


class EventsEyeSchema(BaseModel):
    organizers: List[OrganizerSchema]
    venue: Optional[VenueSchema]
    event: EventSchema
    industries: List[IndustrySchema]