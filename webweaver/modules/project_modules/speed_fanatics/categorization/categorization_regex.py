
import re

from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum, 
    SubCategoryEnum
)


class CategoryRegex:

    regex_mappings = {
        CategoryEnum.BRAKES : re.compile(r'hook.*disc'), #structure a bit clunky.. maybe should be a list of Patterns?
    }    


class SubCategoryRegex:
    ...