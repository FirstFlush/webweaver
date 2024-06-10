import logging
import re
from typing import TYPE_CHECKING
from webweaver.modules.project_modules.speed_fanatics.speed_enums import CategoryEnum
from webweaver.modules.project_modules.speed_fanatics.tire_codes import TireCodeParser, TireSpecs
from webweaver.modules.project_modules.speed_fanatics.product_attributes.attribute_dataclasses import (
    TireAttributeData,
    WheelAttributeData
)

if TYPE_CHECKING:
    from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler

logger = logging.getLogger('scraping')


class AttributeRegex:

    wheel_regex = re.compile(r'(\d{1,2}x\d+(\.\d+)?[\w"]*)\s+(\d{1,2}x\d{2,3}[\w"]*)\s+([+-]?\d{1,3})(?:\s+(\d{2,4}\.\d[\w"]*))?')


class AttributeHandler:

    regex = AttributeRegex

    @property
    def wheel_dict(self) -> dict | None:
        try:
            return self.wheel_attributes.__dict__
        except AttributeError:
            return None


    @property
    def tire_dict(self) -> dict | None:
        try:
            return self.tire_attributes.__dict__
        except AttributeError:
            return None
        

    def __init__(self, category_enum:CategoryEnum, project_handler:"SpeedProjectHandler"=None):
        self.category_enum = category_enum
        self.project_handler = project_handler
        self.wheel_attributes = None
        self.tire_attributes = None
        match self.category_enum:
            case CategoryEnum.TIRES:
                self.tire_attributes = TireAttributeData()
            case CategoryEnum.WHEELS:
                self.wheel_attributes = WheelAttributeData()
            case _:
                raise ValueError(f"category_enum invalid: `{category_enum}`")


    def scrape_tire_data_from_string(self, s, **kwargs):
        """Searches the string, most like product name, for a tire code and if it
        successfully parses the tire code then it populates the tire attributes with
        the data it scraped.
        *Will not override data that has already been populated.
        """
        parser = TireCodeParser(s, use_search=True, **kwargs)
        self.tire_data_from_specs(parser.specs)


    def scrape_wheel_data_from_string(self, product_name:str):
        """This method scrapes the wheel code in the product names on TheWheelShop.ca
        Examples:
            15x6.0 4x100 40
            17x7.5 4x100 40
            22x9.0 6x127mm +45 78
            20x9 5x112 25 72.6
        """
        match = self.regex.wheel_regex.search(product_name.lower())
        if match:
            diameter, width = tuple(match.group(1).split('x'), 1)
            if not self.wheel_attributes.diameter:
                self.wheel_attributes.diameter = diameter
            if not self.wheel_attributes.width:
                self.wheel_attributes.width = width
            if not self.wheel_attributes.bolt_pattern:
                self.wheel_attributes.bolt_pattern = match.group(3)
            if not self.wheel_attributes.offset:
                self.wheel_attributes.offset = match.group(4)
            try:
                if not self.wheel_attributes.centerbore:
                    self.wheel_attributes.centerbore = match.group(5)
            except IndexError:
                pass


    def tire_data_from_specs(self, tire_specs:TireSpecs):
        """Update the tire attributes from the TireSpecs object."""
        if self.category_enum != CategoryEnum.TIRES:
            raise ValueError(f"self.category_enum must be `{CategoryEnum.TIRES}`, not `{self.category_enum}`")
        if tire_specs.TIRE_WIDTH:
            self.tire_attributes.width = tire_specs.TIRE_WIDTH
        if tire_specs.ASPECT_RATIO:
            self.tire_attributes.aspect_ratio = tire_specs.ASPECT_RATIO
        if tire_specs.WHEEL_DIAMETER:
            self.tire_attributes.wheel_diameter = tire_specs.WHEEL_DIAMETER
        if tire_specs.LOAD_INDEX:
            self.tire_attributes.load_index = tire_specs.LOAD_INDEX
        if tire_specs.LOAD_INDEX_DUAL:
            self.tire_attributes.load_index_dual = tire_specs.LOAD_INDEX_DUAL
        if tire_specs.SPEED_RATING:
            self.tire_attributes.speed_rating = tire_specs.SPEED_RATING
        if tire_specs.OVERALL_DIAMETER:
            self.tire_attributes.overall_diameter = tire_specs.OVERALL_DIAMETER
        if tire_specs.SERVICE_TYPE:
            self.tire_attributes.service_type = tire_specs.SERVICE_TYPE



    def final_check(self) -> bool:
        if self.category_enum == CategoryEnum.TIRES:
            return self.final_check_tires()
        elif self.category_enum == CategoryEnum.WHEELS:
            return self.final_check_wheels()
        else:
            msg = f"AttributeHander.final_check() failed due to invalid category enum: {self.category_enum}"
            logger.error(msg)
            return False

    def final_check_tires(self) -> bool:
        """Ensure the essential tire values have been scraped"""
        return bool(
            self.tire_attributes.wheel_diameter and
            self.tire_attributes.width
        )

    def final_check_wheels(self) -> bool:
        """Ensure the essential wheel values have been scraped"""
        return bool(
            self.wheel_attributes.diameter and 
            self.wheel_attributes.width
        )