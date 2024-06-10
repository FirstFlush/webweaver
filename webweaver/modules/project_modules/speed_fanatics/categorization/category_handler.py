from typing import ItemsView
from collections import Counter
from webweaver.modules.project_modules.speed_fanatics.categorization.base_handler import BaseHandler
from webweaver.modules.project_modules.speed_fanatics.categorization.category_keywords import CategoryKeyWords
from webweaver.modules.project_modules.speed_fanatics.categorization.categorization_regex import CategoryRegex

from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum, 
    SubCategoryEnum,
    MatchMode
)
# from webweaver.modules.project_modules.speed_fanatics.speed_mappings import


class CategoryHandler(BaseHandler):

    keywords = CategoryKeyWords
    regex = CategoryRegex

    
    @property
    def keyword_sets(self) -> dict[CategoryEnum, set]:
        keyword_sets = {}
        for category_enum, wordlist_enums_dict in self.keywords.categories.items():
            for wordlist_enum, wordlist in wordlist_enums_dict.items():
                if wordlist_enum == MatchMode.KEYWORDS:
                    keyword_sets[category_enum] = wordlist
        return keyword_sets


    @property
    def substring_sets(self) -> dict[CategoryEnum, set]:
        substring_sets = {}
        for category_enum, wordlist_enums_dict in self.keywords.categories.items():
            for wordlist_enum, wordlist in wordlist_enums_dict.items():
                if wordlist_enum == MatchMode.SUBSTRINGS:
                    substring_sets[category_enum] = wordlist
        return substring_sets


    def get_category_enum(
            self, 
            product_name:str, 
            category_name:str=None, 
            custom_mapping:dict[str, CategoryEnum]=None
    ) -> CategoryEnum:
        """Use a mix of keyword-matching, fuzzy-string-matching, and regex-matching.
        to determine the product's category enum.
        """
        category_enum = None
        if custom_mapping:
            category_enum = custom_mapping.get(category_name)
            if category_enum: 
                return category_enum
        
        product_name = self.normalize_text(product_name)
        category_name = self.normalize_text(category_name)

        category_enum = self.try_keywords(product_name, category_name)
        # self.try_fuzzy_matching()
        # self.try_regex()
        return category_enum if category_enum else CategoryEnum.UNKNOWN



    def try_keywords(self, product_name:str, category_name:str=None) -> CategoryEnum | None:
        """First check if any words in product or category names match any words the category keyword sets.
        Then check if any of the words in category keyword set match any substring in product/category names.
        """
        category_enums = self.check_keywords_in_set(product_name, category_name)
        category_enums.extend(self.keyword_set_substrings(product_name, category_name))
        most_common_enum = Counter(category_enums).most_common(1)    
        return most_common_enum[0][0] if most_common_enum else None




    def check_keywords_in_set(self, product_name:str, category_name:str=None) -> list[CategoryEnum]:
        """Check for direct keyword matches."""
        category_enums = []
        for category_enum, keyword_set in self.keyword_sets.items():
            if self.contains_keywords(product_name, keyword_set):
                category_enums.append(category_enum)
            if category_name:
                if self.contains_keywords(category_name, keyword_set):
                    category_enums.append(category_enum)
        return category_enums


    def keyword_set_substrings(self, product_name:str, category_name:str=None) -> list[CategoryEnum]:
        """Check for substrings"""
        product_name = self.project_handler.fuzzy_handler.preprocess(product_name)
        category_name = self.project_handler.fuzzy_handler.preprocess(category_name)
        category_enums = []
        for category_enum, keyword_set in self.substring_sets.items():
            if self.search_substrings(product_name, keyword_set):
                category_enums.append(category_enum)
            if category_name:
                if self.search_substrings(category_name, keyword_set):
                    category_enums.append(category_enum)
        return category_enums