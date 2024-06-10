from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.dispensary_enum import DispensaryEnum

# This file exists to handle keyword-mapping logic at the dispensary-level
# For example GreenSociety.cc has a cateogry called "$99.99 or Less"
# This category represents ounces of cannabis flower for under $100.
# It wouldn't make sense to put "9999orless" as a keyword to fuzzy-match,
# since that would only apply to this 1 dispensary. So we put that mapping here.


class DispensaryKeywordHandler:

    category_text_to_category_enum = {}
    subcategory_text_to_category_enum = {}
    


class BCBudSupplyHandler(DispensaryKeywordHandler):
    ...


class GreenSocietyHandler(DispensaryKeywordHandler):

    category_text_to_category_enum = {
            '$99.99 or Less' : CategoryEnum.FLOWER,
            'the green room' : CategoryEnum.FLOWER,
            # 'CBD & THC Vape Pens' : CategoryEnum.UNKNOWN,
        }



class DispensaryKeywordMapping:
    
    dispensary_enum_to_keyword_handler:dict[DispensaryEnum, DispensaryKeywordHandler] = {
        DispensaryEnum.GREEN_SOCIETY : GreenSocietyHandler,
        DispensaryEnum.BC_BUD_SUPPLY : BCBudSupplyHandler,
    }