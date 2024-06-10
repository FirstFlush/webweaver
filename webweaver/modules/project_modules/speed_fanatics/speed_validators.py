from webweaver.modules.project_modules.speed_fanatics.speed_regex import SpeedRegex
# from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler
from webweaver.exceptions import PipelineCleaningError
# from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner


class SpeedValidator:

    regex = SpeedRegex
    # project_handler = SpeedProjectHandler() #singleton


# class BrandValidator(SpeedValidator):

#     @classmethod
#     def brand_match(cls, value:str) -> str|None:
#         """Check the brand mapping to see if we already have an instance of this brand."""
#         brand_name_fuzzy = cls.project_handler.fuzzy_handler.preprocess(value)
#         return cls.project_handler.brand_name_to_brand.get(brand_name_fuzzy, value)


class ProductValidator(SpeedValidator):

    @classmethod
    def clean_product_code(cls, value:str) -> str:
        return value.replace('(', '').replace(')', '').strip()


class TireAttributeValidator(SpeedValidator):

    @classmethod
    def utqg(cls, value:str) -> str | None:
        if isinstance(value, str): 
            if value.lower().strip() == 'n/a' or value.lower().strip() == 'tba':
                return None
        return value

    @classmethod
    def width(cls, value:str) -> str | None:
        if value: 
            if float(value) <= 50:
                return cls._inch_to_mm(value)
            else:
                return float(value)
        raise ValueError(f"Tire's width must not be None")


    @staticmethod
    def _inch_to_mm(inches:str) -> float | None:
        """Converts inches to mm"""
        return float(inches) * 25.4


class WheelAttributeValidator(SpeedValidator):

    @classmethod
    def offset(cls, value:str) -> int:
        offset = cls.regex.wheel_offset.sub('', value)
        try:
            return int(offset)
        except (TypeError, ValueError):
            raise PipelineCleaningError(f"Offset value '{value}' invalid.")
        
    @classmethod
    def bolt_pattern(cls, value:str) -> str:
        return value.replace('mm','').lower()
    

    @classmethod
    def load_rating(cls, value:str) -> float|None:
        """Tries to return a float of value stripped of the substring 'kg'.
        If that fails then the assumption is there are 2 values in the 
        string: kg and lb. Next step is perform a regex to extract all
        numbers. If 2 numbers are found, take the lowest because that will
        be kg.
        """
        if not value:
            return None
        try:
            return float(value.replace('kg',''))
        except ValueError:
            load_indices = cls.regex.extract_numbers.findall(value)
            if len(load_indices) != 2:
                raise ValueError(f"WheelAttributeValidation received invalid load_rating string: {value}")
            return min([float(load_index) for load_index in load_indices])