import re
import logging
from typing import Callable
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.mapping.subcategory_keywords import SubCategoryKeyWords, HelperKeywords
from webweaver.modules.project_modules.dispensaries.mapping.base_category_handler import BaseCategoryHandler
from webweaver.modules.project_modules.dispensaries.mapping.category_handler import CategoryHandler
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum


logger = logging.getLogger('scraping')


class SubCategoryRegex:

    prerolls = re.compile(r"pre.*roll", re.IGNORECASE)
    capsules = re.compile(r"gel.*cap|\bcapsules?\b|\bpills?\b")
    carts = re.compile(r"^(?!.*disposable)\b(?:cart(?:s|ridge|ridges)?|pens?)\b")
    htfse = re.compile(r"full.*spectrum|htfse")
    sauce = re.compile(r'^(?!.*\bhtfse\b)(?!.*\bfull.*spectrum\b).*\bsauce\b.*$')
    infused = re.compile(r"moon.*rocks?|\binfused\b")
    indica = re.compile(r"^(?!.*\bhybrid\b).*indica.*$")
    sativa = re.compile(r"^(?!.*\bhybrid\b).*sativa.*$")
    rolling_papers = re.compile(r"^(?!.*\btray\b).*rolling.*$|\bpapers?\b")
    


class SubCategoryHandler(BaseCategoryHandler):
    """Class that links KeyWords, regex patterns, and logic together in order to 
    determine the subcategory of the product scraped.
    
    Each SubCategory in the DB will have a subclass of this class.
    Each subclass (ie FlowerHandler) will have its own subcategory_conditons dictionary.
    This dict maps SubCategoryEnum objects to their evaluation functions.
    Evaluation functions just return true or false. 
    *I will change this to a fuzzy string matching system if the boolean system 
    doesn't work well

    When classmethod get_subcategory runs, it tries every subcategory's function to see
    which returns True and then is classified as that subcategory.
    Since the first True result will exit the function, specialized subcategories should
    come first. For example "preroll indica joints" would match both "preroll" and "indica".
    This should be classified as a preroll product, and so the preroll test must happen before indica.
    
    SubCategory is sorted key words and regex patterns. 
    The key words are stored in sets and used in 2 ways:
        -intersected with a set made of the words in product name
        -iterated, with each key word searched as substring in product name

    """
    REGEX_PATTERNS = SubCategoryRegex
    KEYWORDS = SubCategoryKeyWords


    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        print('dis broke')
        logger.warning(f"{cls.__name__}: get_subcategory method not implemented! Returning SubCategoryEnum.UNKNOWN")
        return SubCategoryEnum.UNKNOWN


    @staticmethod
    def get_subcategory_method(subcategory_enum:SubCategoryEnum) -> Callable | None:
        """Returns the SubCategoryHandler method found in the 
        SubCategoryMethod mapping which corresponds with subcategory_enum."""
        return SubCategoryMethod.subcategory_enum_to_method.get(subcategory_enum)



class AccessoriesHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.ACCESSORIES].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set, category_text):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        return SubCategoryEnum.UNKNOWN
    
    @classmethod
    def rolling_papers(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        # cls.contains_keywords(product_name, keyword_set)
        cls.regex(product_name, cls.REGEX_PATTERNS.rolling_papers)



class BulkHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.BULK].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        return SubCategoryEnum.UNKNOWN


class BundleHandler(SubCategoryHandler):

    category_enum_to_bundle_subcategory_enum = {
        CategoryEnum.ACCESSORIES : SubCategoryEnum.BUNDLE_MISC,
        CategoryEnum.CBD : SubCategoryEnum.BUNDLE_CBD,
        CategoryEnum.CONCENTRATES : SubCategoryEnum.BUNDLE_CONCENTRATES,
        CategoryEnum.EDIBLES : SubCategoryEnum.BUNDLE_EDIBLES,
        CategoryEnum.FLOWER : SubCategoryEnum.BUNDLE_FLOWER,
        CategoryEnum.VAPES : SubCategoryEnum.BUNDLE_VAPES,
        CategoryEnum.UNKNOWN : SubCategoryEnum.BUNDLE_UNKNOWN,
    }


    cross_category_sets_to_subcategory_enum = {
        frozenset({SubCategoryEnum.BUNDLE_VAPES, SubCategoryEnum.BUNDLE_EDIBLES}) : SubCategoryEnum.BUNDLE_VAPES,
        frozenset({SubCategoryEnum.BUNDLE_VAPES, SubCategoryEnum.BUNDLE_CBD}) : SubCategoryEnum.BUNDLE_CBD
    }

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the bundle subcategory by first determining what the CategoryEnum would
        be if it wasn't a bundle.
        """
        # subcategory_enums = []
        # for subcategory_enum, call_method in SubCategoryMethod.subcategory_enum_to_method.items():
        #     ...

        subcategory_enums = CategoryHandler.bundle_category(
            category_text=category_text,
            product_name=product_name,
        )
        subcategory_enums_length = len(subcategory_enums)
        if subcategory_enums_length == 0:
            return SubCategoryEnum.BUNDLE_UNKNOWN
        elif subcategory_enums_length == 1:
            return cls.category_enum_to_bundle_subcategory_enum[subcategory_enums[0]]
        else:
            return SubCategoryEnum.BUNDLE_CROSS_CATEGORY


    @classmethod
    def cross_category(cls, category_enum_bundle:list[CategoryEnum]) -> SubCategoryEnum | None:
        """Check if the combinations of category enums is in our list of forbidden sets"""
        return cls.cross_category_sets_to_subcategory_enum.get(set(category_enum_bundle))
        


class CbdHandler(SubCategoryHandler):


    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.CBD].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set, category_text):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if cls.search_substrings(product_name, SubCategoryKeyWords.keyword_sets[HelperKeywords.FRUIT]):
            return SubCategoryEnum.CBD_EDIBLES

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        return SubCategoryEnum.UNKNOWN


    @classmethod
    def cbd_edibles(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        if cls.contains_keywords_product_or_category(product_name, keyword_set, category_text):
            return True
        return False
        
             

class ConcentratesHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.CONCENTRATES].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        if cls.contains_keywords(product_name, SubCategoryKeyWords.keyword_sets[CategoryEnum.EDIBLES][SubCategoryEnum.OIL]):
            return SubCategoryEnum.OIL

        return SubCategoryEnum.UNKNOWN


    @classmethod
    def htfse(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        if cls.contains_keywords(product_name, keyword_set):
            return True
        if cls.regex(product_name, cls.REGEX_PATTERNS.htfse):
            return True
        return False
    

    @classmethod
    def sauce(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        if cls.contains_keywords(product_name, keyword_set):
            if cls.regex(product_name, cls.REGEX_PATTERNS.sauce):
                return True
        return False


class EdiblesHandler(SubCategoryHandler):


    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.EDIBLES].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set, category_text):
                true_subcategories.append(subcategory_enum)

        print('true_subcategories: ', true_subcategories)
        if len(true_subcategories) > 0:
            return true_subcategories[0]

        if cls.search_substrings(product_name, SubCategoryKeyWords.keyword_sets[HelperKeywords.FRUIT]):
            return SubCategoryEnum.CANDY

        return SubCategoryEnum.UNKNOWN


    @classmethod
    def chocolate(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        return cls.contains_keywords_product_or_category(
            product_name=product_name, 
            keyword_set=keyword_set, 
            category_text=category_text
        )


class FlowerHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []

        keyword_set = SubCategoryKeyWords.keyword_sets[CategoryEnum.FLOWER][SubCategoryEnum.INFUSED]
        method = cls.get_subcategory_method(SubCategoryEnum.INFUSED)
        if method(product_name, keyword_set, category_text):
            true_subcategories.append(SubCategoryEnum.INFUSED)

        keyword_set = SubCategoryKeyWords.keyword_sets[CategoryEnum.FLOWER][SubCategoryEnum.PREROLL]
        method = cls.get_subcategory_method(SubCategoryEnum.PREROLL)
        if method(product_name, keyword_set, category_text):
            true_subcategories.append(SubCategoryEnum.PREROLL)

        keyword_set = SubCategoryKeyWords.keyword_sets[CategoryEnum.FLOWER][SubCategoryEnum.SHAKE]
        method = cls.get_subcategory_method(SubCategoryEnum.SHAKE)
        if method(product_name, keyword_set, category_text):
            true_subcategories.append(SubCategoryEnum.SHAKE)

        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.FLOWER].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set, category_text):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        return SubCategoryEnum.UNKNOWN

    @classmethod
    def hybrid(cls, product_name:str, keyword_set:set[str], category_text:str) -> bool:
        if cls.contains_keywords_product_or_category(
            product_name=product_name,
            keyword_set=keyword_set,
            category_text=category_text
        ):
            return True
        return False


    @classmethod
    def infused(cls, product_name:str, keyword_set:set[str], category_text=None) -> bool:
        if cls.contains_keywords_product_or_category(product_name, keyword_set, category_text):
            return True
        elif cls.regex(product_name, cls.REGEX_PATTERNS.infused):
            return True
        return False

class VapeHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for subcategory_enum, keyword_set in SubCategoryKeyWords.keyword_sets[CategoryEnum.VAPES].items():
            method = cls.get_subcategory_method(subcategory_enum)
            if method(product_name, keyword_set):
                true_subcategories.append(subcategory_enum)
        
        print('true_subcategories: ', true_subcategories)

        if len(true_subcategories) > 0:
            return true_subcategories[0]

        if cls.search_substrings(product_name, SubCategoryKeyWords.keyword_sets[HelperKeywords.FRUIT]):
            return SubCategoryEnum.CARTS

        return SubCategoryEnum.UNKNOWN


class UnknownHandler(SubCategoryHandler):

    @classmethod
    def get_subcategory(cls, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Get the SubCategoryEnum object"""
        true_subcategories = []
        for category_enum, subcategory_enums in SubCategoryKeyWords.keyword_sets.items():
            if isinstance(category_enum, CategoryEnum):
                for subcategory_enum, keyword_set in subcategory_enums.items():
                    if cls.contains_keywords(
                        product_name=product_name,
                        keywords=keyword_set,
                    ):
                        true_subcategories.append(subcategory_enum)
        print('true_subcategories: ', true_subcategories)
        if len(true_subcategories) > 0:
            return true_subcategories[0]

        return SubCategoryEnum.UNKNOWN




class SubCategoryMethod:

    subcategory_enum_to_method:dict[SubCategoryEnum, Callable] = {
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
            SubCategoryEnum.CHOCOLATE : EdiblesHandler.chocolate,
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









































# class SubCategoryHandler(BaseCategoryHandler):
#     """Class that links KeyWords, regex patterns, and logic together in order to 
#     determine the subcategory of the product scraped.
    
#     Each SubCategory in the DB will have a subclass of this class.
#     Each subclass (ie FlowerHandler) will have its own subcategory_conditons dictionary.
#     This dict maps SubCategoryEnum objects to their evaluation functions.
#     Evaluation functions just return true or false. 
#     *I will change this to a fuzzy string matching system if the boolean system 
#     doesn't work well

#     When classmethod get_subcategory runs, it tries every subcategory's function to see
#     which returns True and then is classified as that subcategory.
#     Since the first True result will exit the function, specialized subcategories should
#     come first. For example "preroll indica joints" would match both "preroll" and "indica".
#     This should be classified as a preroll product, and so the preroll test must happen before indica.
    
#     SubCategory is sorted key words and regex patterns. 
#     The key words are stored in sets and used in 2 ways:
#         -intersected with a set made of the words in product name
#         -iterated, with each key word searched as substring in product name
    
#     """
#     subcategory_conditions:dict[SubCategoryEnum, Callable] = {}

#     @classmethod
#     def get_subcategory(cls, product_name:str) -> SubCategoryEnum:
#         """Iterate through the subcategory_conditions dictionary to get 
#         the appropriate subcategory name.
#         """
#         for subcategory, condition in cls.subcategory_conditions.items():
#             if condition(product_name):
#                 return subcategory
        
#         return SubCategoryEnum.UNKNOWN


# class CbdHandler(SubCategoryHandler):

#     subcategory_conditions = {
#         SubCategoryEnum.CBD_CAPSULES: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.capsules),
#         SubCategoryEnum.CBD_EDIBLES: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.cbd_edibles),
#         SubCategoryEnum.CBD_PETS: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.cbd_pets),
#         SubCategoryEnum.CBD_OIL: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.oil)
#     }

# class EdibleHandler(SubCategoryHandler):

#     subcategory_conditions = {
#         SubCategoryEnum.BAKED_GOODS: lambda name: SubCategoryHandler.search_substrings(name, SubCategoryKeyWords.baked_goods),
#         SubCategoryEnum.BEVERAGES: lambda name: SubCategoryHandler.search_substrings(name, SubCategoryKeyWords.beverages),
#         SubCategoryEnum.CANDY: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.candy),
#         SubCategoryEnum.CAPSULES: lambda name: SubCategoryHandler.regex(name, SubCategoryRegex.capsules),
#         SubCategoryEnum.CHOCOLATE: lambda name: SubCategoryHandler.search_substrings(name, SubCategoryKeyWords.chocolate),
#         SubCategoryEnum.OIL: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.oil),
#         SubCategoryEnum.TINCTURES: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords.tinctures),
#     }


# class FlowerHandler(SubCategoryHandler):

#     subcategory_conditions = {
#         SubCategoryEnum.INFUSED: lambda name: SubCategoryEnum.INFUSED.value in name,
#         SubCategoryEnum.PREROLL: lambda name: SubCategoryHandler.regex(name, SubCategoryRegex.prerolls),
#         SubCategoryEnum.INDICA: lambda name: SubCategoryEnum.INDICA.value in name,
#         SubCategoryEnum.SATIVA: lambda name: SubCategoryEnum.SATIVA.value in name,
#         SubCategoryEnum.HYBRID: lambda name: SubCategoryEnum.HYBRID.value in name,
#     }


# class VapeHandler(SubCategoryHandler):

#     subcategory_conditions = {
#         SubCategoryEnum.CARTS: lambda name: SubCategoryHandler.regex(name, SubCategoryRegex.carts),
#         SubCategoryEnum.DISPOSABLE: lambda name: SubCategoryHandler.contains_keywords(name, SubCategoryKeyWords) 
#         SubCategoryEnum.BATTERIES: ...,
#     }