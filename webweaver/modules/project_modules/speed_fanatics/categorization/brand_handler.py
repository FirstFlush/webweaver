# from typing import TYPE_CHECKING
from tortoise.exceptions import IntegrityError, TransactionManagementError
from tortoise.transactions import in_transaction
from webweaver.modules.project_modules.speed_fanatics.models import Brand
from webweaver.modules.project_modules.speed_fanatics.categorization.base_handler import BaseHandler

# if TYPE_CHECKING:
#     from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler


class BrandHandler(BaseHandler):

    generic_words = {
        'tires',
        'tire',
        'products',
        'wheel',
        'wheels',
        'and',
        'company',
        'parts',
        'the',
        'ltd',
    }

    def normalize_brand_name(self, brand_name:str, apply_fuzzy_prepocessing:bool=True) -> str:
        """Strip the generic words from the brand's name. 
        Apply fuzzy preprocessing if necessary.
        """
        stripped = ' '.join([word for word in brand_name.split() if word not in self.generic_words])
        if apply_fuzzy_prepocessing:
            return self.project_handler.fuzzy_handler.preprocess(stripped)
        else:
            return stripped


    async def get_or_create_brand(self, brand_name:str) -> tuple[Brand, bool]:
        """Check the brand mapping to see if we already have an instance of this brand.
        If the brand already exists, return it. If not, create a new brand.
        """
        is_created = False
        brand_name_normalized = self.normalize_brand_name(brand_name)
        brand = self.project_handler.brand_name_to_brand.get(brand_name_normalized)
        if not brand:
            brand, is_created = await Brand.get_or_create(brand_name=brand_name.strip())

        return brand, is_created


    def match_brand(self, value:str) -> str|None:
        """Check the brand mapping to see if we already have an instance of this brand."""
        brand_name_fuzzy = self.project_handler.fuzzy_handler.preprocess(value)
        return self.project_handler.brand_name_to_brand.get(brand_name_fuzzy, value)

