from pydantic import BaseModel, validator

from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class FastcoSchema(BaseModel):
    # add your validation schema here
    ...
