from webweaver.modules.project_modules.dispensaries.weed_project_handler import WeedProjectHandler
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_mapping import VariationEnum
from webweaver.modules.project_modules.dispensaries.data.products.models import Dispensary
from webweaver.modules.project_modules.dispensaries.dispensary_enum import DispensaryEnum


class WeedSpiderMixin:
    """Logic and tools for scraping dispensaries
    Gives access to the categorization and variation mapping framework,
    to (hopefully) reliably determine a product's category, subcategory, 
    and variation, if possible.
    
    PRODUCT_BUNDLE_PATTERN regex should match the following:
        -Anything between 'mix' and 'match'
        -Anything between 'buy' and 'get'
        -Anything between 'give' and 'away'
        -the word 'pack' preceded by any amount of digits (4 pack, 5 pack, etc)
        -the stand-alone words 'bundle', 'free', 'bogo'
    """
    project_handler = WeedProjectHandler() 


    def check_strain(self, product_name:str) -> tuple:
        return self.project_handler.fuzzy_handler.best_match(product_name)


    def get_variation_enum(self, variation_value:str) -> VariationEnum:
        """Return the product variation's Enum, if any is found."""
        return self.project_handler.mapping.get_variation(variation_value)


    async def get_dispensary(self) -> Dispensary:
        """Get the Dispensary model object associated with 
        this Spider's SpiderAsset model.
        """
        return await self.spider_asset.dispensary


    async def get_dispensary_enum(self) -> DispensaryEnum:
        dispensary = await self.get_dispensary()   
        return dispensary.dispensary_enum


    def get_categories(self, category_text:str, product_name:str) -> tuple[CategoryEnum, SubCategoryEnum]:
        """Get Category and SubCategory enums"""
        return self.project_handler.mapping.get_categories(
            category_text=category_text, 
            product_name=product_name,
            spider_asset=self.spider_asset,
        )


    def get_category(self, category_text:str, product_name:str=None) -> CategoryEnum:
        """Checks the product category mapping to determine the category"""
        return self.project_handler.mapping.get_category(
            category_text = category_text, 
            product_name = product_name
        )

    def get_subcategory(self, category_enum:CategoryEnum, product_name:str, category_text:str=None) -> SubCategoryEnum:
        """Checks the product subcategory mapping to determine the subcategory"""
        return self.project_handler.mapping.get_subcategory(
            category_enum = category_enum,
            product_name = product_name,
            category_text = category_text
        )



    def is_bundle(self, s:str) -> bool:
        """Checks if the product listing is in fact a bundle of 
        products using regex.
        """
        return self.project_handler.mapping.is_bundle(s)


    # def log_module_error(self, product_name:str):
    #     """Make use of the spider's module-level logging system to log the irregularity
    #     of no category (or subcategory) being found."""
    #     if hasattr(self, 'log') and callable(self.log):
    #         self.log(f"No category found for product: {product_name}")
    #     return


    # def _map_category(self, s:str, subcategory:bool=False) -> str|None:
    #     """Map the product's listed category/subcategory to its approporiate 
    #     match in our schema.
    #     """
    #     if subcategory:
    #         return self.project_handler.mapping.SUBCATEGORY_MAP.get(s.lower())
    #     else:
    #         return self.project_handler.mapping.CATEGORY_MAP.get(s.lower())