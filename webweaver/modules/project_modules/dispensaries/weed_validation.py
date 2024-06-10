from decimal import Decimal
from pydantic import BaseModel, ValidationError, root_validator
from typing import List, Optional

from webweaver.modules.project_modules.dispensaries.weed_enums import BudRatingEnum, VariationTypeEnum
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.dispensary_enum import DispensaryEnum
from webweaver.modules.project_modules.dispensaries.mapping.variation.variation_mapping import VariationEnum



class VariationType(BaseModel):
    type_name: str
    data_type: VariationTypeEnum


class ProductValidation(BaseModel):
    dispensary: DispensaryEnum
    category: CategoryEnum
    subcategory: SubCategoryEnum
    variations: Optional[List[VariationEnum]]
    product_name: str




class ProductPriceValidation(BaseModel):
    product: ProductValidation
    variation: Optional[List[VariationEnum]]
    price: Decimal
    is_sale: bool


class BudRatingValidation(BaseModel):
    product: ProductValidation
    rating: BudRatingEnum



class BundleValidation(BaseModel):
    dispensary: DispensaryEnum
    products: Optional[List[ProductValidation]]
    category: CategoryEnum
    subcategor: SubCategoryEnum
    bundle_name: str


class BundlePriceValidation(BaseModel):
    bundle: BundleValidation
    price: Decimal
    is_sale: bool



class WeedValidationSchema(BaseModel):
    product: Optional[ProductPriceValidation]
    bundle: Optional[BundleValidation]

    @root_validator(pre=True)
    def check_one_none(cls, values):
        """Uses an XOR operator to ensure either Product or Bundle is None.
        Enforces a one-or-the-other pattern.
        """
        product, bundle = values.get('product'), values.get('bundle')
        # if (product is None and bundle is None) or (product is not None and bundle is not None):
        if not (product is None) ^ (bundle is None):
            raise ValueError('One of either "product" or "bundle" must be provided.')
        return values




class ProductDescriptionValidation(BaseModel):
    product_name: str
    text: str
