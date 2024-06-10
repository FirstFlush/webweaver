from webweaver.project.project_base import ProjectHandler
from webweaver.modules.project_modules.dispensaries.dispensary_enum import DispensaryEnum
from webweaver.modules.project_modules.dispensaries.dispensary_keyword_modules.dispensary_keyword_handler import DispensaryKeywordHandler
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.mapping.weed_mapper import WeedMapper
from webweaver.modules.project_modules.dispensaries.data.strains.models import Strain
from webweaver.modules.project_modules.dispensaries.weed_pipeline import WeedPipeline
from webweaver.modules.project_modules.dispensaries.registry.dispensary_registry import (
    DispensaryRegistry, 
    DispensaryRegistryBuilder
)
from webweaver.modules.project_modules.dispensaries.fuzzy_strain_handler import FuzzyStrainHandler
from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.webscraping.spiders.models import SpiderAsset


class ProjectHandlerInterface:
    """This is the interface for WeedMapper (horrible class name, tells you nothing)
    to interact with ProjectHandler and it's goodies such as fuzzy string handler
    and dispensary registry.

    When WeedMapper wants to query the dispensary registry, it does so through
    the ProjectHandlerInterface.
    """
    def __init__(self, project_handler:"WeedProjectHandler"):
        self.project_handler = project_handler


    def get_pipeline_class(self) -> Pipeline:
        """Returns the pipeline class."""
        return self.project_handler.pipeline_class


    def check_strain(self, s:str, cutoff:float=100.0) -> bool:
        """Fuzzy-string matching to check if the strain name matches in our DB"""
        score = self.project_handler.fuzzy_handler.best_match(s)[1]
        print('fuzzy match score: ', score)
        return bool(score >= cutoff)


    def get_dispensary_enum(self,spider_asset:SpiderAsset) -> DispensaryEnum | None:
        dispensary = self.project_handler.dispensary_registry.spider_asset_to_dispensary.get(spider_asset)
        if dispensary:
            return dispensary.dispensary_enum


    def get_dispensary_handler(
            self, 
            dispensary_enum:DispensaryEnum
    ) -> DispensaryKeywordHandler | None:
        """Get the DispensaryKeywordHandler object that is mapped to the DispensaryEnum in the 
        DispensaryKeywordMapping class.
        """
        return self.project_handler.dispensary_registry.dispensary_enum_to_keyword_handler.get(dispensary_enum)


    def get_enum_overrides(
        self,
        s: str,
        dispensary_handler:DispensaryKeywordHandler
    ) -> tuple[CategoryEnum|None, SubCategoryEnum|None]:
        """Returns a tuple of (CategoryEnum, SubCategoryEnum) if either enum
        is found in the dispensary keyword mappings. Usually will return (None, None)
        """
        category_enum = dispensary_handler.category_text_to_category_enum.get(s)
        subcategory_enum = dispensary_handler.subcategory_text_to_category_enum.get(s)
        return category_enum, subcategory_enum



# class PipelineInterface(ProjectHandlerInterface):
#     """Interface for the Pipeline object to get/set
#     attributes of WeedProjectHandler.
#     """



class WeedProjectHandler(ProjectHandler):

    _instance = None
    mapping = None
    dispensary_registry = {}
    fuzzy_handler = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


    def create_interface(self) -> ProjectHandlerInterface:
        return ProjectHandlerInterface(self)


    async def initialize_project(self):
        """Factory method for instantiating the WeedProjectHandler object."""
        self.dispensary_registry = await self._build_dispensary_registry()
        self.fuzzy_handler = await self._get_fuzzy_handler()
        self.interface = self.create_interface()
        self.mapping = WeedMapper(handler_interface = self.interface)
        self.pipeline_class = WeedPipeline


    @staticmethod
    async def _get_fuzzy_handler() -> FuzzyStrainHandler:
        return await FuzzyStrainHandler.get_handler_from_model(Strain, 'name')

    @staticmethod
    async def _build_dispensary_registry() -> DispensaryRegistry:
        return await DispensaryRegistryBuilder().build_dispensary_registry()