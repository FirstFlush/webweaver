from pydantic import BaseModel, validator

from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class AutoEvolutionSchema(BaseModel):

    vehicle_make: str
    vehicle_model: str