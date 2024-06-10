from typing import TYPE_CHECKING, Optional
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum, CategoryEnumMap
from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_handler import VariationHandler
from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_mapping import VariationEnum
from webweaver.modules.project_modules.dispensaries.mapping.category_handler import CategoryHandler, CategoryRegex
from webweaver.modules.project_modules.dispensaries.mapping.subcategory_handler import (
    SubCategoryHandler,
    AccessoriesHandler,
    BulkHandler,
    BundleHandler,
    CbdHandler,
    ConcentratesHandler,
    EdiblesHandler,
    FlowerHandler,
    VapeHandler,
    UnknownHandler
)
from webweaver.modules.project_modules.dispensaries.dispensary_keyword_modules.dispensary_keyword_handler import (
    DispensaryEnum, 
    DispensaryKeywordHandler
)
from webweaver.webscraping.spiders.models import SpiderAsset

if TYPE_CHECKING:
    from webweaver.modules.project_modules.dispensaries.weed_project_handler import ProjectHandlerInterface


class WeedMapper:
    """This class serves as a spider's means of interfacing
    with the following classes:
        CategoryHandler, 
        SubCategoryHandler, 
        VariationHandler,
    The functionality of those classes can be used by the spider/pipeline
    to quickly determine category, subcategory, and variation value.
    """
    category_enum_to_subcategory_handler_map:dict[CategoryEnum, SubCategoryHandler] = {
        CategoryEnum.ACCESSORIES : AccessoriesHandler,
        CategoryEnum.BULK : BulkHandler,
        CategoryEnum.BUNDLE : BundleHandler,
        CategoryEnum.CBD : CbdHandler,
        CategoryEnum.CONCENTRATES : ConcentratesHandler,
        CategoryEnum.EDIBLES : EdiblesHandler,
        CategoryEnum.FLOWER : FlowerHandler,
        CategoryEnum.VAPES : VapeHandler,
        CategoryEnum.UNKNOWN : UnknownHandler,
    }




    def __init__(self, handler_interface:"ProjectHandlerInterface"):
        self.handler_interface = handler_interface





    @staticmethod
    def standardize_text(text:str|None) -> str|None:
        """Replae the weird dashes with the regular dash."""
        return text.replace('–','-').replace('—','-').lower() if text else None


    def get_categories(self, category_text:str, product_name:str, spider_asset:SpiderAsset) -> tuple[CategoryEnum, SubCategoryEnum]:
        """Returns a tuple of the CategoryEnum & SubCategoryEnum.        
        Processing steps:
        
        """
        category_enum = WeedMapper.get_category(
            category_text=self.standardize_text(category_text), 
            product_name=self.standardize_text(product_name)
        )
        subcategory_enum = WeedMapper.get_subcategory(
            category_enum = category_enum,
            product_name = self.standardize_text(product_name),
            category_text = self.standardize_text(category_text)
        )

        if category_enum == CategoryEnum.UNKNOWN:
            if self.handler_interface.check_strain(product_name):
                category_enum = CategoryEnum.FLOWER

        if category_enum == CategoryEnum.BULK and subcategory_enum == SubCategoryEnum.UNKNOWN:
            if self.handler_interface.check_strain(product_name):
                subcategory_enum = SubCategoryEnum.BULK_FLOWER


        category_enum_check = CategoryEnumMap.subcategory_enum_to_category_enum.get(subcategory_enum)
        if category_enum != category_enum_check and category_enum_check is not None:
            category_enum = CategoryEnumMap.subcategory_enum_to_category_enum[subcategory_enum]

        # Check dispensary-level keyword filtering
        # possibly move this to the start, and skip the rest of the logic if somethings found
        category_override, subcategory_override = self.check_dispensary_keyword_overrides(
            s = category_text.strip(),
            spider_asset = spider_asset,
        )
        if category_override:
            category_enum = category_override
        if subcategory_override:
            subcategory_enum = subcategory_override

        return category_enum, subcategory_enum



    def check_dispensary_keyword_overrides(
            self, 
            s:str, 
            spider_asset:SpiderAsset
        ) -> tuple[Optional[CategoryEnum], Optional[SubCategoryEnum]]:
        """The main function in WeedMapper for handling dispensary-level keyword overrides
        of CategoryEnum & SubCategoryEnum.
        """
        dispensary_enum = self.handler_interface.get_dispensary_enum(spider_asset)

        dispensary_handler = self.handler_interface.get_dispensary_handler(dispensary_enum) \
            if dispensary_enum else None
        if dispensary_handler:
            return self.handler_interface.get_enum_overrides(
                s=s,
                dispensary_handler=dispensary_handler
            )
        return (None, None)


    @classmethod
    def get_category(cls, category_text:str, product_name:str=None) -> CategoryEnum:
        """Calls CategoryHandler get_category() method"""
        try:
            return CategoryHandler.get_category(
                category_text = cls.standardize_text(category_text),
                product_name = cls.standardize_text(product_name)
            )
        except AttributeError:
            return CategoryEnum.UNKNOWN


    @classmethod
    def is_bundle(cls, s:str) -> bool:
        """With this function a spider can use the 'is_bundle' regex pattern directly,
        instead of having to perform category enumeration.
        """
        return bool(CategoryHandler.regex(s, CategoryHandler.REGEX_PATTERNS.bundle))


    @classmethod
    def get_subcategory(cls, category_enum:CategoryEnum, product_name:str, category_text:str|None) -> SubCategoryEnum:
        """Use the category_enum_to_subcategory_handler mapping to call the 
        get_subcategory() method from the appropriate SubCategoryHandler class
        """
        subcategory_handler = cls.category_enum_to_subcategory_handler_map[category_enum]
        category_text = '' if not category_text else category_text
        try:
            return subcategory_handler.get_subcategory(
                product_name=cls.standardize_text(product_name),
                category_text=cls.standardize_text(category_text)
            )
        except AttributeError:
            return SubCategoryEnum.UNKNOWN


    @classmethod
    def get_variation(cls, variation_value:str) -> VariationEnum:
        """Gets the product variation enum using the VariationHandler"""
        return VariationHandler.get_variation(cls.standardize_text(variation_value))







# CATEGORIES & SUB-CATEGORIES
#     accessories
#         clothing
#         grinders
#         lighters
#         misc
#         pipes
#         rollies
#     bulk
#         bulk concentrates
#         bulk edibles
#         bulk flower
#         bulk hash
#     cbd
#         cbd capsules
#         cbd edibles
#         cbd tinctures
#         cbd oil (also tears?)
#         cbd pets
#         cbd vapes
#         cbd isolate
#     concentrates
#         budder
#         diamonds
#         distillate
#         htfse
#         hash
#         kief
#         live resin
#         phoenix tears
#         rosin
#         shatter
#     flower
#         hybrid
#         indica
#         infused (ie moon rocks)
#         preroll
#         sativa
#     vapes
#         batteries
#         carts
#         disposable
#     edibles
#         candy/gummies
#         capusules
#         chocolate
#         drinks
#         baked goods
#         oils/tinctures
#     unknown
