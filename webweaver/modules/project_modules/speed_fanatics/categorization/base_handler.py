import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler


class BaseHandler:
    """Category and SubCategory Handler classes will inherit this functionality.
    This class is just some tools for parsing the product name against regex
    patterns and keywords to determine the product's category or subcategory.
    """
    keywords = None

    def __init__(self, project_handler:"SpeedProjectHandler"):
        self.project_handler = project_handler

    def normalize_text(self, text:str|None) -> str | None:
        """Replae the weird dashes with the regular dash, lowercase and strip."""
        return text.replace('–','-').replace('—','-').lower().strip() if text else None

    def regex_search(self, s:str, pattern:re.Pattern) -> bool:
        """Calls the pattern.search() method on the string"""
        return bool(pattern.search(s))

    def search_substrings(self, s:str, keywords:set[str]) -> bool:
        """Check if each keyword is a substring in `s`"""
        for keyword in keywords:
            if keyword in s:
                return True
        return False


    def contains_keywords(self, s: str, keywords: set[str]) -> bool:
        """Returns True if any keywords are present in the product name"""
        product_name_words = set(s.split())
        return bool(product_name_words.intersection(keywords))
    