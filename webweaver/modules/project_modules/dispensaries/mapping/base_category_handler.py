import re

class BaseCategoryHandler:


    @staticmethod
    def regex(product_name:str, pattern:re.Pattern) -> bool:
        """Calls the pattern.search() method on the string"""
        return bool(pattern.search(product_name))


    @staticmethod
    def contains_keywords(product_name: str, keywords: set[str], category_text:str=None) -> bool:
        """Returns True if any keywords are present in the product name"""
        title_words = set(product_name.split())
        return bool(title_words.intersection(keywords))
    

    @classmethod
    def contains_keywords_product_or_category(
        cls, 
        product_name:str, 
        keyword_set:set[str], 
        category_text:str
    ):
        if cls.contains_keywords(product_name, keyword_set):
            return True
        elif cls.contains_keywords(category_text, keyword_set):
            return True
        return False


    @staticmethod
    def search_substrings(product_name:str, keywords:set[str], category_text:str=None) -> bool:
        """Check if each keyword is a substring in the """
        for keyword in keywords:
            if keyword in product_name:
                return True
        return False
