from tortoise.models import Model
import spacy

from webweaver.webscraping.fuzzy_matching.fuzzy_handler import FuzzyHandler
from webweaver.modules.project_modules.dispensaries.data.strains.models import Strain
from webweaver.modules.project_modules.dispensaries.data.strains.enum import CannabisTypeEnum
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import SubCategoryEnum, CategoryEnum


class FuzzyStrainHandler(FuzzyHandler):

    async def add_strain_to_db(
            self, 
            strain_name:str, 
            subcategory_enum: SubCategoryEnum,
            product_description:str=None,
        ) -> Strain:
        """Creates a new Strain object in our table of cannabis strains.
        
        TODO: There is a lot more interesting stuff to do with this.
        effects/flavors/ailments can potentially be parsed from the 
        product description.
        """

        return await Strain.create(
            name = strain_name,
            strain_type = self.get_cannabis_type(subcategory_enum)
        )
        
    def get_cannabis_type(self, subcategory_enum:SubCategoryEnum) -> CannabisTypeEnum:
        match subcategory_enum:
            case SubCategoryEnum.HYBRID:
                return CannabisTypeEnum.HYBRID
            case SubCategoryEnum.INDICA:
                return CannabisTypeEnum.INDICA
            case SubCategoryEnum.SATIVA:
                return CannabisTypeEnum.HYBRID
            case _:
                return CannabisTypeEnum.UNKNOWN
            


