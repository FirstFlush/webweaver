from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum, CategoryEnumMap
from webweaver.modules.project_modules.dispensaries.data.products.models import (
    Category, 
    SubCategory,
    Dispensary,
    VariationType,
    Variation
)
from webweaver.modules.project_modules.dispensaries.data.strains.models import Strain
from webweaver.project.project_registry_base import ProjectRegistry
from webweaver.modules.project_modules.dispensaries.dispensary_keyword_modules.dispensary_keyword_handler import DispensaryKeywordMapping
from webweaver.modules.project_modules.dispensaries.weed_enums import VariationTypeEnum

from webweaver.webscraping.registry.scraping_registry import scraping_registry#, SpiderRegistryItem
from webweaver.webscraping.spiders.models import SpiderAsset


class DispensaryRegistryBuilder:



    def __init__(self):
        self.category_enum_to_model = {}
        self.subcategory_enum_to_model = {}
        self.spider_asset_to_dispensary = {}
        self.variation_enum_to_model = {}
        self.variationtype_enum_to_model = {}

    async def _populate_spider_asset_to_dispensary(self):
        """Populates value with dict[SpiderAsset, Dispensary]"""
        for _, spider_registry_item in scraping_registry.registry.items():
            spider_asset:SpiderAsset = spider_registry_item.spider_asset
            dispensary:Dispensary = await spider_asset.dispensary
            self.spider_asset_to_dispensary[spider_asset] = dispensary


    async def _populate_var_mapping(self):
        ...

    async def _populate_vartype_mapping(self) -> dict[VariationTypeEnum, VariationType]:
        ...
        
        # for var_type in await VariationType.all():
        #     if 

        # NOTE do i need this mapping? 
        # - this is already mapped at the DB level
        # - Variation already getting mapped to VariationTypeEnum
        bleh = {
            VariationTypeEnum.GRAMS : float,
            VariationTypeEnum.COLOR : str,
            VariationTypeEnum.ML : int,
            VariationTypeEnum.SIZE_NUM : float,
            VariationTypeEnum.SIZE_STR : str,
            VariationTypeEnum.UNKNOWN : str,
        }


    # def _populate_enum_to_model(enum:Enum, objs:list[Model], attribute_name:str):
    #     for obj in objs:
    #         for enum_obj in enum:
    #             if 


    def _populate_category_mapping(self, categories:list[Category]):
        for category in categories:
            for category_enum in CategoryEnum:
                if category.category_name == category_enum.value:
                    self.category_enum_to_model[category_enum] = category
        self.category_enum_to_model[CategoryEnum.UNKNOWN] = None


    def _populate_subcategory_mapping(self, subcategories:list[SubCategory]):
        for subcategory in subcategories:
            for subcategory_enum in SubCategoryEnum:
                if subcategory.subcategory_name == subcategory_enum.value:
                    self.subcategory_enum_to_model[subcategory_enum] = subcategory


    async def build_dispensary_registry(self) -> "DispensaryRegistry":
        """ Build the dispensary registry by populating category and subcategory,
        then creating a DispensaryRegistry object with the following:
            - category enums to category models,
            - subcategory enums to subcategory models,
            - dispensaries-to-handlers mappings
        """
        categories = await Category.filter(is_active=True)
        subcategories = await SubCategory.filter(is_active=True)
        self._populate_category_mapping(categories)
        self._populate_subcategory_mapping(subcategories)
        await self._populate_spider_asset_to_dispensary()

        print('registry SA to dispensary: ', self.spider_asset_to_dispensary)

        return DispensaryRegistry(
            spider_asset_to_dispensary=self.spider_asset_to_dispensary,
            category_enum_to_model=self.category_enum_to_model,
            subcategory_enum_to_model=self.subcategory_enum_to_model,
        )





class DispensaryRegistry(ProjectRegistry):
    """This registry will act as a shared-state for all dispensary webscrapers.
    
    Dispensary Registry uses:
    -map of dispensary model object (or id) to custom dispensary-level handler class.
    
    -maps category/subcategory enums to their respective model objects.
    -map variation enums to a variation model object? 
        -i like this idea better than creating a new variation object for every single product's every single variation.
    -set of strains, preprocessed for fuzzy-matching.
    -some spacy/NER rule sets of some kind when i actually learn a thing about NER

    Requirements:
        -map dispensary id to additional functionality such as special mappings
        for dispensary-specific categories.
            Example:
                greensociety.cc has category "$99.00 or Less"
                This category is all cheap flower, with ounces for $99 or less.
                So we map "$99.00 or Less" to CategoryEnum.FLOWER, but ONLY when
                scraping greensociety.cc

    Structure:
        - dict mapping dispensary ID to class containing dispensary-level rulesets
        - set of weed strain names, preprocessed for fuzzy-matching
    """
    def __init__(
            self,
            spider_asset_to_dispensary:dict[SpiderAsset, Dispensary],
            category_enum_to_model:dict[CategoryEnum, Category],
            subcategory_enum_to_model:dict[SubCategoryEnum, SubCategory],
        ):
        self.spider_asset_to_dispensary = spider_asset_to_dispensary
        self.dispensary_enum_to_keyword_handler = DispensaryKeywordMapping.dispensary_enum_to_keyword_handler
        self.category_enum_to_model = category_enum_to_model
        self.subcategory_enum_to_model = subcategory_enum_to_model
