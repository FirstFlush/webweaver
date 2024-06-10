from pydantic import BaseModel, validator

from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class SoulPPSchema(BaseModel):
    # add your validation schema here
    ...
