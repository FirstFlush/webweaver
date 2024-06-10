from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from webweaver.common.enums import FileFormatEnum


class SpiderAssetIdSchema(BaseModel):
    id: int


class CampaignIdSchema(BaseModel):
    id: int


class LaunchCampaignSchema(BaseModel):
    id: int
    file_format: Optional[FileFormatEnum]


class CampaignsSchema(BaseModel):
    id: int
    campaign_name: Optional[str] = None
    is_recurring: bool


class ParameterValueSchema(BaseModel):
    value: str


class SpiderParamSchema(BaseModel):
    param_name: str
    param_type: str
    param_description:Optional[str] = None
    param_values: List[ParameterValueSchema]

    @validator('param_type', pre=True)
    def transform_enum_to_string(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value


class SpiderCampaignSchema(BaseModel):
    spider_name: str = Field(..., max_length=255)
    domain: str = Field(..., max_length=255)
    is_active: Optional[bool]
    description: Optional[str] = Field(..., max_length=2048)
    params: List[SpiderParamSchema]


class CampaignSchema(BaseModel):
    campaign_name: Optional[str] = None
    is_recurring: bool
    spiders: List[SpiderCampaignSchema]


class SpiderParameterSchema(BaseModel):
    param_name: str
    param_type: str
    param_description:Optional[str] = None

    @validator('param_type', pre=True)
    def transform_enum_to_string(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value
    

class CreateParamsSchema(BaseModel):
    spider_id: int
    params: List[SpiderParameterSchema]    


class SpiderAssetSchema(BaseModel):
    id: Optional[int] = None
    spider_name: str = Field(..., max_length=255)
    domain: str = Field(..., max_length=255)
    is_active: Optional[bool]
    description: Optional[str] = Field(..., max_length=2048)

    class Config:
        exclude_unset = True


class SpiderAssetDetailSchema(SpiderAssetSchema):
    params: Optional[List[SpiderParameterSchema]]





class ScrapeModuleTablesSchema(BaseModel):
    table_name: str


class JobSchema(BaseModel):
    id: int
    scraped_records: int
    date_scraped: datetime
    tables: Optional[List[ScrapeModuleTablesSchema]]
    campaign: Optional[CampaignsSchema]


class JobsSchema(BaseModel):
    id: int
    date_scraped: datetime
    campaign_id: Optional[int]


class SelectParamsSchema(BaseModel):
    spider_name: str
    params: Optional[List[SpiderParameterSchema]]


class ParamKeyValueSchema(BaseModel):
    param_name: str
    param_value: str


class LaunchSpiderSchema(BaseModel):
    id: int
    file_format: Optional[FileFormatEnum]
    scrape_job_id: Optional[int] 
    params: Optional[List[ParamKeyValueSchema]]