from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from webweaver.config import SPIDER_DATA_BATCH_SIZE


@dataclass
class SpiderData:
    """Data holding class, serving as the container for 
    scraped data passed from SpiderLauncher to PipelineListener, 
    through the async Queue.
    """
    data: dict[str, Any]
    spider_id: int


# class SpiderDataBatch:
#     """This class holds batches of SpiderData, received in the PipelineListener.
#     When a batch reaches the batch size limit, it is passed to the appropriate
#     pipeline module for processing.
#     """
#     batch_data:list[SpiderData] = []

#     def count(self) -> int:
#         """Counts the # of SpiderData objects in the batch"""
#         return len(self.batch_data)

#     def reset_batch(self):
#         """Empties the list of SpiderData"""
#         self.batch_data = []
#         return


# class BatchRegistry:
#     """Registry of SpiderDataBatches to be used by the PipelineListener. As data 
#     comes in from the queue, it will be stored in batches before being processed
#     and saved in the DB. This registry will allow the PipelineListener to know
#     which pipeline module to instantiate for each batch. 
#     """

#     batch_size_limit = SPIDER_DATA_BATCH_SIZE #100, for now

#     def __init__(self):
#         self.batches = defaultdict(SpiderDataBatch)

#     def add_data(self, spider_data:SpiderData):
#         """Appends SpiderData to the appropriate SpiderDataBatch."""
#         self.batches[spider_data.spider_id].batch_data.append(spider_data.data)
#         return

#     def is_batch_full(self, spider_id:int) -> bool:
#         """Check if the SpiderDataBatch has reached the batch_size_limit value."""
#         if self.batches[spider_id].count() >= self.batch_size_limit:
#             return True
#         return False





















# class SpiderData:
#     """Data holding class, serving as the container for 
#     scraped data passed from SpiderLauncher to PipelineListener, 
#     through the async Queue.
#     """
#     def __init__(
#             self, 
#             data:dict, 
#             spider_id: int, 
#             spider_name:str, 
#             is_complete: bool = False
#             ):
#         self.data = data
#         self.spider_id = spider_id
#         self.spider_name = spider_name
#         self.is_complete = is_complete





# class SpiderDataChunk:
    
#     def __init__(self, schema:BaseModel, data:dict):
#         """A chunk of data, representing a coupled-pairing of 
#         the scraped data and the schema for the table the data 
#         is being supplied to.
#         """
#         self.schema = schema
#         self.data = data


# class SpiderData:
#     """Data holding class, serving as the container for 
#     scraped data passed from SpiderLauncher to PipelineListener, 
#     through the async Queue.
#     """
#     def __init__(self,
#                  chunks: list[SpiderDataChunk],
#                  spider_id: int,
#                  is_complete: bool = False
#                  ):
#         self.chunks = chunks
#         self.spider_id = spider_id
#         self.is_complete = is_complete



# {
#     {
#         schema: CompanySchema,
#         data: {
#                company_name,
#                address,
#                website,
#         }
#     },
#     {
#         schema: ReviewSchema,
#         data: {
#             review_count,
#             review_score,
#         }
#     }
# }