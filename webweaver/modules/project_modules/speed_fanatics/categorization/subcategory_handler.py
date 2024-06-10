from collections import Counter

from webweaver.modules.project_modules.speed_fanatics.categorization.base_handler import BaseHandler
from webweaver.modules.project_modules.speed_fanatics.categorization.subcategory_ruleset import SubCategoryRuleset
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum, 
    SubCategoryEnum,
    MatchMode
)


class SubCategoryHandler(BaseHandler):
    """Attempts to determine SubCategory by fuzzy matching, regex, and keyword checking"""

    ruleset = SubCategoryRuleset

    def get_rules(self, category_enum:CategoryEnum, match_mode:MatchMode)-> dict[SubCategoryEnum, set | list]:
        """Returns a set/list of keywords, substrings, or regex patterns 
            -should this method return a dict with values of type set for 
            keywords/substrings (yes) and a list for regex? (maybe no)
        """
        rules = {}
        if category_enum != CategoryEnum.UNKNOWN:
            for subcategory_enum, match_mode_dict in self.ruleset.category_enum_to_subcategory_rules[category_enum].items():
                for match_mode_enum, wordlist in match_mode_dict.items():
                    if match_mode_enum == match_mode:
                        rules[subcategory_enum] = wordlist
        else:
            for _category_enum, subcategory_enums in self.ruleset.category_enum_to_subcategory_rules.items():
                for subcategory_enum, match_mode_dict in subcategory_enums.items():
                    for match_mode_enum, wordlist in match_mode_dict.items():
                        if match_mode_enum == match_mode:
                            rules[subcategory_enum] = wordlist
        return rules



    def keyword_sets(self, category_enum:CategoryEnum) -> dict[SubCategoryEnum, set | list]:
        keyword_sets = {}
        if category_enum != CategoryEnum.UNKNOWN:
            for subcategory_enum, wordlist_enums_dict in self.ruleset.category_enum_to_subcategory_rules[category_enum].items():
                for wordlist_enum, wordlist in wordlist_enums_dict.items():
                    if wordlist_enum == MatchMode.KEYWORDS:
                        keyword_sets[subcategory_enum] = wordlist
        else:
            for _category_enum, subcategory_enums in self.ruleset.category_enum_to_subcategory_rules.items():
                for subcategory_enum, wordlist_enums_dict in subcategory_enums.items():
                    for wordlist_enum, wordlist in wordlist_enums_dict.items():
                        if wordlist_enum == MatchMode.KEYWORDS:
                            keyword_sets[subcategory_enum] = wordlist

        return keyword_sets


    def substring_sets(self, category_enum:CategoryEnum) -> dict[SubCategoryEnum, set]:
        substring_sets = {}
        if category_enum != CategoryEnum.UNKNOWN:
            for subcategory_enum, wordlist_enums_dict in self.ruleset.category_enum_to_subcategory_rules[category_enum].items():
                for wordlist_enum, wordlist in wordlist_enums_dict.items():
                    if wordlist_enum == MatchMode.SUBSTRINGS:
                        substring_sets[subcategory_enum] = wordlist
        else:
            for _category_enum, subcategory_enums in self.ruleset.category_enum_to_subcategory_rules.items():
                for subcategory_enum, wordlist_enums_dict in subcategory_enums.items():
                    for wordlist_enum, wordlist in wordlist_enums_dict.items():
                        if wordlist_enum == MatchMode.SUBSTRINGS:
                            substring_sets[subcategory_enum] = wordlist

        return substring_sets


    def get_subcategory_enum(
            self,
            product_name:str, 
            category_enum:CategoryEnum, 
            category_name:str=None,
            custom_mapping:dict[str, SubCategoryEnum]=None
    ) -> SubCategoryEnum:
    
        if custom_mapping:
            subcategory_enum = custom_mapping.get(category_name)
            if subcategory_enum: 
                return subcategory_enum

        product_name = self.normalize_text(product_name)
        category_name = self.normalize_text(category_name)

        subcategory_enum = self.try_keywords_and_substrings(
            product_name=product_name,
            category_enum=category_enum,
            category_name=category_name,
        )
        if subcategory_enum == SubCategoryEnum.UNKNOWN or subcategory_enum == None:
            subcategory_enum = self.force_subcategory(category_enum)

        return subcategory_enum if subcategory_enum else SubCategoryEnum.UNKNOWN


    def try_keywords_and_substrings(self, product_name:str, category_enum:CategoryEnum, category_name:str=None) -> SubCategoryEnum | None:
        """First check if any words in product or category names match any words the category keyword sets.
        Then check if any of the words in category keyword set match any substring in product/category names.
        """
        subcategory_enums = self.check_keywords_in_set(product_name, category_enum, category_name)
        subcategory_enums.extend(self.keyword_set_substrings(product_name, category_enum, category_name))
        most_common_enum = Counter(subcategory_enums).most_common(1)    

        return most_common_enum[0][0] if most_common_enum else None


    def try_regex(self, product_name:str, category_enum:CategoryEnum) -> SubCategoryEnum | None:
        """Iterate through the rules and try the regex patterns. If one matches,
        return the corresponding SubCategoryEnum
        """
        for subcategory_enum, regex_list in self.get_rules(
            category_enum=category_enum, 
            match_mode=MatchMode.REGEX
        ).items():
            for regex_pattern in regex_list:
                if self.regex_search(s=product_name, pattern=regex_pattern):
                    return subcategory_enum


    def check_keywords_in_set(self, product_name:str, category_enum:CategoryEnum, category_name:str=None) -> list[SubCategoryEnum]:
        subcategory_enums = []
        for subcategory_enum, keyword_set in self.keyword_sets(category_enum).items():
            if self.contains_keywords(product_name, keyword_set):
                subcategory_enums.append(subcategory_enum)
            if category_name:
                if self.contains_keywords(category_name, keyword_set):
                    subcategory_enums.append(subcategory_enum)
        return subcategory_enums


    def keyword_set_substrings(self, product_name:str, category_enum:CategoryEnum, category_name:str=None) -> list[SubCategoryEnum]:

        product_name = self.project_handler.fuzzy_handler.preprocess(product_name)
        category_name = self.project_handler.fuzzy_handler.preprocess(category_name)
        subcategory_enums = []
        for subcategory_enum, keyword_set in self.substring_sets(category_enum).items():
            if self.search_substrings(product_name, keyword_set):
                subcategory_enums.append(subcategory_enum)
            if category_name:
                if self.search_substrings(category_name, keyword_set):
                    subcategory_enums.append(subcategory_enum)
        return subcategory_enums


    def force_subcategory(self, category_enum:CategoryEnum) -> SubCategoryEnum:
        """If CategoryEnum is determined but SubCategoryEnum is unknown, we force
        it to one of the generic subcategories
        """
        match category_enum:
            case CategoryEnum.WHEEL_ACCESSORIES:
                return SubCategoryEnum.WHEEL_MISC
            case CategoryEnum.TIRE_ACCESSORIES:
                return SubCategoryEnum.TIRES_MISC
            case CategoryEnum.WHEELS:
                return SubCategoryEnum.WHEELS_AUTOMOTIVE
            case _:
                return SubCategoryEnum.UNKNOWN
