from typing import Callable

from modules.project_modules.dispensaries.mapping.category_enums import SubCategoryEnum
from modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum
from modules.project_modules.dispensaries.mapping.category_handler import CategoryMethods
from modules.project_modules.dispensaries.mapping.subcategory_handler import (
    AccessoriesHandler,
    BulkHandler,
    BundleHandler,
    CbdHandler,
    ConcentratesHandler,
    EdiblesHandler,
    FlowerHandler,
    VapeHandler,
)

class CategoryMapping:


    category_enum_to_bundle_subcategory_enum = {
        CategoryEnum.ACCESSORIES : SubCategoryEnum.BUNDLE_MISC,
        CategoryEnum.CBD : SubCategoryEnum.BUNDLE_CBD,
        CategoryEnum.CONCENTRATES : SubCategoryEnum.BUNDLE_CONCENTRATES,
        CategoryEnum.EDIBLES : SubCategoryEnum.BUNDLE_EDIBLES,
        CategoryEnum.FLOWER : SubCategoryEnum.BUNDLE_FLOWER,
        CategoryEnum.VAPES : SubCategoryEnum.BUNDLE_VAPES,
        CategoryEnum.UNKNOWN : SubCategoryEnum.BUNDLE_UNKNOWN,
    }


    subcategory_enum_to_category_enum = {
        # Accessories
        SubCategoryEnum.CLOTHING : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.GRINDERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.LIGHTERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.PIPES : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.ROLLING_PAPERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.MISC : CategoryEnum.ACCESSORIES,
        # Bulk
        SubCategoryEnum.BULK_CONCENTRATES : CategoryEnum.BULK,
        SubCategoryEnum.BULK_EDIBLES : CategoryEnum.BULK,
        SubCategoryEnum.BULK_FLOWER : CategoryEnum.BULK,
        SubCategoryEnum.BULK_HASH : CategoryEnum.BULK,
        # Bundle
        SubCategoryEnum.BUNDLE_CBD : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_CONCENTRATES : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_CROSS_CATEGORY : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_EDIBLES : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_FLOWER : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_MISC : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_UNKNOWN : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_VAPES : CategoryEnum.BUNDLE,
        # CBD
        SubCategoryEnum.CBD_CAPSULES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_EDIBLES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_ISOLATE : CategoryEnum.CBD,
        SubCategoryEnum.CBD_OIL : CategoryEnum.CBD,
        SubCategoryEnum.CBD_PETS : CategoryEnum.CBD,
        SubCategoryEnum.CBD_TINCTURES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_TOPICALS : CategoryEnum.CBD,
        SubCategoryEnum.CBD_VAPES : CategoryEnum.CBD,
        # Concentrates
        SubCategoryEnum.BUBBLE_HASH : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.BUDDER : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.DIAMONDS : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.DISTILLATE : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.HTFSE : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.HASH : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.KIEF : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.LIVE_RESIN: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.PHOENIX_TEARS: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.ROSIN: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.SAUCE: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.SHATTER: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.WAX: CategoryEnum.CONCENTRATES,
        # Edibles
        SubCategoryEnum.BAKED_GOODS : CategoryEnum.EDIBLES,
        SubCategoryEnum.BEVERAGES : CategoryEnum.EDIBLES,
        SubCategoryEnum.CANDY : CategoryEnum.EDIBLES,
        SubCategoryEnum.CAPSULES : CategoryEnum.EDIBLES,
        SubCategoryEnum.CHOCOLATE : CategoryEnum.EDIBLES,
        SubCategoryEnum.OIL : CategoryEnum.EDIBLES,
        SubCategoryEnum.TINCTURES : CategoryEnum.EDIBLES,
        # Flower
        SubCategoryEnum.HYBRID : CategoryEnum.FLOWER,
        SubCategoryEnum.INDICA : CategoryEnum.FLOWER,
        SubCategoryEnum.INFUSED : CategoryEnum.FLOWER,
        SubCategoryEnum.PREROLL : CategoryEnum.FLOWER,
        SubCategoryEnum.SATIVA : CategoryEnum.FLOWER,
        SubCategoryEnum.SHAKE : CategoryEnum.FLOWER,
        # Vapes
        SubCategoryEnum.BATTERIES : CategoryEnum.VAPES,
        SubCategoryEnum.CARTS : CategoryEnum.VAPES,
        SubCategoryEnum.DISPOSABLE : CategoryEnum.VAPES,
    }



    category_enum_to_category_method = {
        CategoryEnum.ACCESSORIES    : CategoryMethods.accessories,
        CategoryEnum.BULK           : CategoryMethods.bulk,
        CategoryEnum.BUNDLE         : CategoryMethods.bundle,
        CategoryEnum.CBD            : CategoryMethods.cbd,
        CategoryEnum.CONCENTRATES   : CategoryMethods.concentrates,
        CategoryEnum.EDIBLES        : CategoryMethods.edibles,
        CategoryEnum.FLOWER         : CategoryMethods.flower,
        CategoryEnum.VAPES          : CategoryMethods.vapes,
    }



    subcategory_enum_to_subcategory_method:dict[SubCategoryEnum, Callable] = {
            # Accessories
            SubCategoryEnum.CLOTHING : AccessoriesHandler.contains_keywords,
            SubCategoryEnum.GRINDERS : AccessoriesHandler.contains_keywords,
            SubCategoryEnum.LIGHTERS : AccessoriesHandler.contains_keywords,
            SubCategoryEnum.MISC : AccessoriesHandler.contains_keywords,
            SubCategoryEnum.PIPES : AccessoriesHandler.contains_keywords,
            SubCategoryEnum.ROLLING_PAPERS : AccessoriesHandler.rolling_papers,
            # Bulk
            SubCategoryEnum.BULK_CONCENTRATES : BulkHandler.contains_keywords,
            SubCategoryEnum.BULK_EDIBLES : BulkHandler.contains_keywords,
            SubCategoryEnum.BULK_FLOWER : BulkHandler.contains_keywords,
            SubCategoryEnum.BULK_HASH : BulkHandler.contains_keywords,
            # Bundle
            # SubCategoryEnum.BUNDLE_CBD : BundleHandler.contains_keywords,
            # CBD
            SubCategoryEnum.CBD_CAPSULES : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_EDIBLES : CbdHandler.cbd_edibles,
            SubCategoryEnum.CBD_ISOLATE : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_OIL : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_PETS : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_TINCTURES : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_TOPICALS : CbdHandler.contains_keywords,
            SubCategoryEnum.CBD_VAPES : CbdHandler.contains_keywords,
            # Concentrates
            SubCategoryEnum.BUDDER : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.DIAMONDS : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.DISTILLATE : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.HTFSE : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.HASH : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.KIEF : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.LIVE_RESIN : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.PHOENIX_TEARS : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.ROSIN : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.SAUCE : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.SHATTER : ConcentratesHandler.contains_keywords,
            SubCategoryEnum.WAX : ConcentratesHandler.contains_keywords,
            # Edibles
            SubCategoryEnum.BAKED_GOODS : EdiblesHandler.contains_keywords,
            SubCategoryEnum.BEVERAGES : EdiblesHandler.contains_keywords,
            SubCategoryEnum.CANDY : EdiblesHandler.contains_keywords,
            SubCategoryEnum.CAPSULES : EdiblesHandler.contains_keywords,
            SubCategoryEnum.CHOCOLATE : EdiblesHandler.contains_keywords,
            SubCategoryEnum.OIL : EdiblesHandler.contains_keywords,
            SubCategoryEnum.TINCTURES : EdiblesHandler.contains_keywords,
            # Flower
            SubCategoryEnum.HYBRID : FlowerHandler.hybrid,
            SubCategoryEnum.INDICA : FlowerHandler.contains_keywords_product_or_category,
            SubCategoryEnum.INFUSED : FlowerHandler.infused,
            SubCategoryEnum.PREROLL : FlowerHandler.contains_keywords,
            SubCategoryEnum.SATIVA : FlowerHandler.contains_keywords_product_or_category,
            SubCategoryEnum.SHAKE : FlowerHandler.contains_keywords,
            # Vapes
            SubCategoryEnum.BATTERIES : VapeHandler.contains_keywords,
            SubCategoryEnum.CARTS : VapeHandler.contains_keywords,
            SubCategoryEnum.DISPOSABLE : VapeHandler.contains_keywords,
        }