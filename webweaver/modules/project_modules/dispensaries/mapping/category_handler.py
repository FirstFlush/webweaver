import re

from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum
from webweaver.modules.project_modules.dispensaries.mapping.category_keywords import CategoryKeyWords
from webweaver.modules.project_modules.dispensaries.mapping.base_category_handler import BaseCategoryHandler


class CategoryRegex:
    """Regex patterns:
    beverages       match beverage(s), dont match if cbd  
    bundle
    moon_rocks      moon..rock(s)
    htfse           full..spectrum, htfse, don't match if vape(s)
    """
    beverages = re.compile(r"^(?!.*\bcbd\b).*\bbeverages?\b.*$")
    bundle = re.compile(r"mix.*match|buy.*get|give.*away|\b\d+\s+pack\b|\bbundles?\b|\bfree\b|\bbogo\b", re.IGNORECASE)
    cbd_no_thc = re.compile(r"^(?!.*thc).*cbd")
    moon_rocks = re.compile(r"moon.*rocks?")
    htfse  = re.compile(r"^(?!.*vapes?)(?:full.*spectrum|htfse)")
    final_check_flower = re.compile(r"\bcannabis\b|\bgreens?\b|\bweed\b|\bmarijuana\b|\bbuds?\b|mary.*jane")


class CategoryMethods:
    """This class is where we write our rules for how each category will determine
    if the category name belongs to it"""

    KEYWORD_SETS = CategoryKeyWords
    REGEX_PATTERNS = CategoryRegex

    @classmethod
    def accessories(cls, category_text:str, product_name:str=None) -> bool:
        return CategoryHandler.contains_keywords(category_text, cls.KEYWORD_SETS.accessories)

    @classmethod
    def bulk(cls, category_text:str, product_name:str=None) -> bool:
        return CategoryHandler.contains_keywords(category_text, cls.KEYWORD_SETS.bulk)


    @classmethod
    def bundle(cls, category_text:str, product_name:str=None) -> bool:
        """Run the bundle regex pattern on both product name and category name."""
        if CategoryHandler.regex(product_name, pattern=cls.REGEX_PATTERNS.bundle):
            return True
        elif CategoryHandler.regex(category_text, pattern=cls.REGEX_PATTERNS.bundle):
            return True
        return False
    

    @classmethod
    def cbd(cls, category_text:str, product_name:str=None) -> bool:
        if CategoryHandler.search_substrings(category_text, cls.KEYWORD_SETS.cbd):
            return True
        elif CategoryHandler.contains_keywords(product_name, cls.KEYWORD_SETS.cbd):
            return True
        return False

    @classmethod
    def concentrates(cls, category_text:str, product_name:str=None) -> bool:
        return CategoryHandler.contains_keywords(category_text, cls.KEYWORD_SETS.concentrates)

    @classmethod
    def edibles(cls, category_text:str, product_name:str=None) -> bool:
        if CategoryHandler.contains_keywords_product_or_category(
            product_name=product_name,
            keyword_set=cls.KEYWORD_SETS.edibles,
            category_text=category_text
        ):
            return True
        # elif CategoryHandler.regex(category_name, CategoryMethods.REGEX_PATTERNS.beverages):
        #     return True
        elif CategoryHandler.regex(product_name, CategoryMethods.REGEX_PATTERNS.beverages):
            return True
        return False
    

    @classmethod
    def flower(cls, category_text:str, product_name:str=None) -> bool:
        if CategoryHandler.contains_keywords(category_text, cls.KEYWORD_SETS.flower):
            return True
        # Check if the product name has moon rocks in it.
        if CategoryHandler.regex(product_name, cls.REGEX_PATTERNS.moon_rocks):
            return True
        return False

    # @classmethod
    # def flower(cls, category_name:str, product_name:str=None) -> bool:
    #     return CategoryHandler.contains_keywords(category_name, cls.KEYWORD_SETS.flower)
    
    @classmethod
    def vapes(cls, category_text:str, product_name:str=None) -> bool:
        return CategoryHandler.contains_keywords(category_text, cls.KEYWORD_SETS.vapes)


    @classmethod
    def final_check(cls, category_text:str, product_name:str=None) -> CategoryEnum | None:
        """If the CategoryEnum has not been determined by any methods in the 
        CategoryEnum:Method mapping, this is a place for final tests to determine
        a category. Otherwise CategoryEnum.UNKNOWN will be chosen.
        """
        if CategoryHandler.regex(category_text, cls.REGEX_PATTERNS.final_check_flower) \
                or 'haze' in product_name:
            return CategoryEnum.FLOWER



class CategoryHandler(BaseCategoryHandler):
    """This class holds the logic, key words, and regex patterns for determining
    the product's category.

    Possible categories:
        Accessories
        Bulk
        CBD
        Concentrates
        Edibles
        Flower
        Vapes
        Unknown
    """
    REGEX_PATTERNS = CategoryRegex

    category_method_map = {
        CategoryEnum.ACCESSORIES    : CategoryMethods.accessories,
        CategoryEnum.BULK           : CategoryMethods.bulk,
        CategoryEnum.BUNDLE         : CategoryMethods.bundle,
        CategoryEnum.CBD            : CategoryMethods.cbd,
        CategoryEnum.CONCENTRATES   : CategoryMethods.concentrates,
        CategoryEnum.EDIBLES        : CategoryMethods.edibles,
        CategoryEnum.FLOWER         : CategoryMethods.flower,
        CategoryEnum.VAPES          : CategoryMethods.vapes,
        # CategoryEnum.UNKNOWN        : CategoryMethods.unknown,
    }

    @classmethod
    def get_category(cls, category_text:str, product_name:str=None) -> CategoryEnum:
        """Iterates the category/method map and calls all the methds until
        one returns True. If none are True, returns default UNKNOWN.
        """
        for category_enum, class_method in cls.category_method_map.items():
            if class_method(category_text, product_name):
                return category_enum
        category_enum = CategoryMethods.final_check(
            category_text=category_text,
            product_name=product_name
        )
        return category_enum if category_enum else CategoryEnum.UNKNOWN




    @classmethod
    def bundle_category(cls, category_text:str, product_name:str) -> list[CategoryEnum]:
        """Determine the bundle's subcategory by first determining 
        what category the bundle would be, if it were not a bundle.

        Returning a list of CategoryEnums, that way we can identify cross-category promotions.
        """
        # true_categories = []
        # for category_enum, class_method in cls.category_method_map.items():
        #     if category_enum == CategoryEnum.BUNDLE or category_enum == CategoryEnum.BULK:
        #         continue

        #     if cls.contains_keywords(product_name, CategoryKeyWords)

        #     true_categories.append(category_enum)
        # return true_categories

        true_categories = []
        for category_enum, class_method in cls.category_method_map.items():
            if category_enum == CategoryEnum.BUNDLE or category_enum == CategoryEnum.BULK:
                continue
            if class_method(category_text, product_name):
                true_categories.append(category_enum)

        if len(true_categories) == 0:
            for category_enum, class_method in cls.category_method_map.items():
                if category_enum == CategoryEnum.BUNDLE or category_enum == CategoryEnum.BULK:
                    continue
                if class_method(product_name, category_text):
                    true_categories.append(category_enum)


        # print('bundle true: ', true_categories)
        return true_categories


















# class CategoryHandler(BaseCategoryHandler):
#     """This class holds the logic, key words, and regex patterns for determining
#     the product's category.

#     Possible categories:
#         Accessories
#         Bulk
#         CBD
#         Concentrates
#         Edibles
#         Flower
#         Vapes
#         Unknown
#     """
#     regex = CategoryRegex
#     KEYWORD_SETS = CategoryKeyWords

#     def __init__(self, product_name:str, category_name:str):
#         self.product_name = product_name
#         self.category_name = category_name
#         self.category_method_map = {
#             CategoryEnum.ACCESSORIES    : self._accessories(),
#             CategoryEnum.CBD            : self._cbd(),
#             CategoryEnum.CONCENTRATES   : self._concentrates(),
#             CategoryEnum.EDIBLES        : self._edibles(),
#             CategoryEnum.FLOWER         : self._flower(),
#             CategoryEnum.VAPES          : self._vapes(),
#         }

#     def _accessories(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.accessories)

#     def _bulk(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.bulk)

#     def _cbd(self) -> bool:
#         return self.search_substrings(self.product_name, self.KEYWORD_SETS.cbd)
        
#     def _concentrates(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.concentrates)

#     def _edibles(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.edibles)
    
#     def _flower(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.flower)
    
#     def _vapes(self) -> bool:
#         return self.contains_keywords(self.product_name, self.KEYWORD_SETS.vapes)


#     def get_category(self) -> CategoryEnum:
#         """Iterates the category/method map and calls all the methds until
#         one returns True. If none are True, returns default UNKNOWN.
#         """
#         for category_enum, func in self.category_method_map.items():
#             if func():
#                 return category_enum
#         return CategoryEnum.UNKNOWN