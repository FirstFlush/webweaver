from pydantic import BaseModel, validator
from typing import Optional
from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class CompanySchema(BaseModel):
    company_name: str
    address: str
    phone: Optional[str]
    url: Optional[str]

    _trim_url = validator("url", pre=True)(PipelineCleaner.url_domain)


class ReviewSchema(BaseModel):
    review_count: int
    review_score: float


    _to_float = validator("review_score", pre=True)(PipelineCleaner.to_float)
    _to_int = validator("review_count", pre=True)(PipelineCleaner.to_int)


class GoogleMapsSchema(BaseModel):
    company: CompanySchema
    review: ReviewSchema
