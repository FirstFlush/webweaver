import re

from webweaver.modules.project_modules.speed_fanatics.product_attributes.attribute_handler import AttributeHandler
from webweaver.modules.project_modules.speed_fanatics.constants import MIN_PRICE
from webweaver.modules.project_modules.speed_fanatics.tire_codes import TireCodeParser
from webweaver.modules.project_modules.speed_fanatics.speed_mappings import SpeedMapping
from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    SupplierEnum, 
    DataTypeEnum, 
    TireAttributeEnum, 
    WheelAttributeEnum,
    CategoryEnum,
    SubCategoryEnum
)
from webweaver.modules.project_modules.speed_fanatics.speed_regex import SpeedRegex
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier, 
    VariationType,
    Category,
    SubCategory
)



class SpeedSpiderMixin:
    """Individual Spider's means of getting/setting in the SpeedProjectHandler"""

    project_handler = SpeedProjectHandler()  # singleton
    

    @property
    def supplier(self) -> Supplier:
        return self.project_handler.spider_asset_to_supplier[self.spider_asset]


    @property
    def speed_mapping(self) -> SpeedMapping:
        """Because self.project_handler.mapping is a bore to write"""
        return self.project_handler.mapping


    def attribute_handler(self, category_enum:CategoryEnum) -> "AttributeHandler":
        """Instantiate a new AttributeHandler object"""
        return self.project_handler.attribute_handler(
            category_enum=category_enum, 
            project_handler=self.project_handler
        )


    def get_categories(
            self,
            product_name:str,
            category_name:str=None,
            category_mapping:dict[str, CategoryEnum]=None,
            subcategory_mapping:dict[str, SubCategoryEnum]=None,
    ) -> tuple[Category, SubCategory]:
        """Returns both the CategoryEnum and SubCategoryEnum for the product."""
        category_enum = self.get_category_enum(
            product_name=product_name,
            category_name=category_name,
            custom_mapping=category_mapping
        )
        subcategory_enum = self.get_subcategory_enum(
            product_name=product_name,
            category_enum=category_enum,
            category_name=category_name,
            custom_mapping=subcategory_mapping
        )
        category_enum, subcategory_enum = self._category_check(
            category_enum=category_enum, 
            subcategory_enum=subcategory_enum
        )

        category = self.get_category_from_enum(category_enum)
        subcategory = self.get_subcategory_from_enum(subcategory_enum)
        
        return category, subcategory


    def _category_check(
            self, 
            category_enum:CategoryEnum, 
            subcategory_enum:SubCategoryEnum
    ) -> tuple[CategoryEnum, SubCategoryEnum]:
        """If category is unknown but subcategory is known then we can determine
        the category using the mapping of subcategory_enum_to_category_enum.
        """
        if category_enum == CategoryEnum.UNKNOWN and subcategory_enum != SubCategoryEnum.UNKNOWN:
            category_enum = self.project_handler.mapping.subcategory_enum_to_category_enum[subcategory_enum]
        return category_enum, subcategory_enum



    def get_subcategory_enum(
            self, 
            product_name:str, 
            category_enum:CategoryEnum,
            category_name:str=None, 
            custom_mapping:dict[str,SubCategoryEnum] = None
    ) -> SubCategoryEnum: 
        return self.project_handler.subcategory_handler.get_subcategory_enum(
            product_name=product_name,
            category_enum=category_enum,
            category_name=category_name,
            custom_mapping=custom_mapping
        )


    def get_category_enum(
            self, 
            product_name:str, 
            category_name:str=None, 
            custom_mapping:dict[str,CategoryEnum] = None
        ) -> CategoryEnum:
        """Primary means of the the Spider to interface with the CategoryHandler."""
        
        return self.project_handler.category_handler.get_category_enum(
            product_name=product_name, 
            category_name=category_name,
            custom_mapping=custom_mapping
        )
    

    def get_category_from_enum(self, category_enum:CategoryEnum) -> Category:
        category = self.project_handler.category_enum_to_category.get(category_enum)
        if not category:
            category = self.project_handler.category_enum_to_category[CategoryEnum.UNKNOWN]
        return category


    def get_subcategory_from_enum(self, subcategory_enum:SubCategoryEnum) -> SubCategory:
        subcategory = self.project_handler.subcategory_enum_to_subcategory.get(subcategory_enum)
        if not subcategory:
            subcategory = self.project_handler.subcategory_enum_to_subcategory[SubCategoryEnum.UNKNOWN]
        return subcategory






    def parse_wheel_size(self, wheel_size_string:str) -> tuple[str, str]:
        """Industry-standard wheel size examples: 15x8, 17x9.5

        This format needs to be split in 2 because the first number is
        diameter and the 2nd number is width.
        """
        wheel_size_list = wheel_size_string.lower().split(sep='x')
        wheel_diameter = wheel_size_list[0].strip()
        wheel_width = wheel_size_list[1].strip()
        return wheel_diameter, wheel_width


    def tire_attributes_from_tire_code(self, tire_code:str) -> dict[TireAttributeEnum, str]:
        """Uses a regex to parse the tire code for the following:
            -width
            -aspect ratio
            -wheel diameter
            -load index
            -speed rating

        Tire code examples:
            245/60R18 105T
            305/30ZR19 102W
            315/70R17 121/118S
            185R14C 102/100Q
            195/70R15C 104/102R
            35X12.5R20 125R
        """
        tire_code = tire_code.upper().strip().replace('(','').replace(')','')
        if tire_code[0].isalpha():
            if tire_code[1].isalpha():
                service_type = tire_code[:2]
                tire_code = tire_code[2:]
            else:
                service_type = tire_code[0]
                tire_code = tire_code[1:]
        else:
            service_type = None

        match = self.project_handler.regex.tire_code.match(tire_code)
        if match:
            tire_code_dict = {
                TireAttributeEnum.SERVICE_TYPE : service_type,
                TireAttributeEnum.TIRE_WIDTH : match.group(1),
                TireAttributeEnum.ASPECT_RATIO : match.group(2),
                TireAttributeEnum.WHEEL_DIAMETER : match.group(3),
                TireAttributeEnum.LOAD_INDEX : match.group(4),
                TireAttributeEnum.LOAD_INDEX_DUAL : match.group(5),
                TireAttributeEnum.SPEED_RATING : match.group(6),
            }
        else:
            match = self.project_handler.regex.tire_code_2.match(tire_code)
            if match:
                tire_code_dict =  {
                    TireAttributeEnum.TIRE_WIDTH : match.group(1),
                    TireAttributeEnum.ASPECT_RATIO : None,
                    TireAttributeEnum.WHEEL_DIAMETER : match.group(3),
                    TireAttributeEnum.SERVICE_TYPE : match.group(4),
                    TireAttributeEnum.LOAD_INDEX : match.group(5),
                    TireAttributeEnum.LOAD_INDEX_DUAL : match.group(6),
                    TireAttributeEnum.SPEED_RATING : match.group(7),
                }
            else:
                match = self.project_handler.regex.tire_code_3.match(tire_code)
                if match:
                    tire_code_dict = {
                        TireAttributeEnum.TIRE_WIDTH : match.group(1),
                        TireAttributeEnum.ASPECT_RATIO : match.group(2),
                        TireAttributeEnum.WHEEL_DIAMETER : match.group(3),
                        TireAttributeEnum.SERVICE_TYPE : match.group(4),
                        TireAttributeEnum.LOAD_INDEX : match.group(5),
                        TireAttributeEnum.LOAD_INDEX_DUAL : match.group(6),
                        TireAttributeEnum.SPEED_RATING : match.group(7),
                    }
                else:
                    match = self.project_handler.regex.tire_code_offroad.match(tire_code)
                    if match:
                        width_inches = float(match.group(2))
                        tire_code_dict = {
                            TireAttributeEnum.OVERALL_DIAMETER : match.group(1),
                            TireAttributeEnum.ASPECT_RATIO : None,
                            TireAttributeEnum.TIRE_WIDTH : str(self.inch_to_mm(width_inches)) if width_inches <= 50 else str(width_inches),
                            TireAttributeEnum.WHEEL_DIAMETER : match.group(4),
                            TireAttributeEnum.SERVICE_TYPE : match.group(5),
                            TireAttributeEnum.LOAD_INDEX : match.group(6),
                            TireAttributeEnum.SPEED_RATING : match.group(7),
                        }
                    else:
                        match = self.project_handler.regex.tire_code_reinf.match(tire_code)
                        if match:
                            tire_code_dict = {
                                TireAttributeEnum.SERVICE_TYPE : service_type,
                                TireAttributeEnum.TIRE_WIDTH : match.group(1),
                                TireAttributeEnum.ASPECT_RATIO : match.group(2),
                                TireAttributeEnum.WHEEL_DIAMETER : match.group(3),
                                TireAttributeEnum.LOAD_INDEX : None,
                                TireAttributeEnum. SPEED_RATING : None,
                            }
                        else:
                            raise self.errors.WebScrapingError(f"Can't parse tire code: {tire_code}")
        return tire_code_dict



    # def lb_to_kg(self, lb:float) -> float:
    #     return lb * 0.453592

    def lbs_to_kg(self, value:str) -> str:
        """Convert lb to kg but keep it as a string"""
        return str(float(value) * 0.45359237)


    def inch_to_mm(self, inches:str|float) -> str:
        """Converts inches to mm"""
        return str(float(inches) * 25.4)

    


    def get_variation_enum_from_text(self, text:str) -> DataTypeEnum:
        variation_enum = self.speed_mapping.text_to_data_type.get(self.fuzzing.preprocess(text))
        return variation_enum if variation_enum else DataTypeEnum.STRING


    def strip_nondigits(self, s:str) -> str:
        """This will strip out all non-digit characters"""
        return ''.join([char for char in s if char.isdigit() or char == '.'])


    def split_wheel_size(self, wheel_size:str) -> tuple[str, str] | tuple[None, None]:
        """When given a "wheel_size" value it returns a 
        tuple of (wheel_diameter, wheel_width)
        
        If ValueError, we just skip this product. too much headache right now.
        Some products will have multiple wheel sizes: '5x127/5x139.7'. Currently
        I don't have a good way to scrape/pipeline these without an overhaul. There
        aren't many products like this so for now we will just log them and pass.
        """
        try:
            return tuple([self.strip_nondigits(value) for value in wheel_size.lower().split('x',1)])
        except ValueError:
            return None, None

    def price_range_split(self, price_range:str, separator:str=" - ") -> list[str, str]:
        """Splits a price range like '$140 - $180' into 2 separate prices,
        to be saved as 2 separate price objects.
        """
        return price_range.split(separator, maxsplit=2)


    def convert_price(self, price:str) -> float | None:
        """Uses regex to convert scraped price text to a float.

        *Normally this kind of thing would be handled in the pipeline, 
        specifically by the PipelineCleaner class.
        I am giving Spider this functionality because if price on product card 
        is below the MIN_PRICE value, then we can skip scraping the PDP
        """
        regex_match = re.search(self.project_handler.regex.price_regex, price)
        if regex_match:
            return float(regex_match.group(0).replace(',',''))            


    def check_min_price(self, price:float) -> bool:
        """Checks if the price scraped is >= MIN_PRICE constant"""
        price_float = self.convert_price(price)
        if price_float:
            return bool(price_float >= MIN_PRICE)
        return False


# class SpeedPipelineMixin:
#     """So far this class exists for SpeedPipeline to easily access 
#     the mapping of {SpiderAsset : Supplier}
#     """
#     proejct_handler = SpeedProjectHandler()  # singleton

#     @property
#     def supplier(self) -> Supplier:
#         spider_asset = self.get_spider_asset()
#         return self.proejct_handler.spider_asset_to_supplier[spider_asset]
    

#     @property
#     def supplier_enum(self) -> SupplierEnum:
#         return self.supplier.supplier_enum.value