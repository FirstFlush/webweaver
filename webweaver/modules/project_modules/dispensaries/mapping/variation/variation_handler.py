# from typing import Any
from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_mapping import (
    VariationMap, 
    VariationEnum
)


class VariationHandler:
    """Handler class for anything wanting to make use of the VariationMap structure."""
    mapping = VariationMap

    @classmethod
    def get_variation(cls, variation_value:str) -> VariationEnum:
        """passes the variation value through self.variation_map to
        return the variation value enum.
        """
        variation_enum = cls.mapping.VARIATION_MAP.get(variation_value)
        if variation_enum:
            return variation_enum
        return VariationEnum.UNKNOWN