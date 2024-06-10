from decimal import Decimal
from pydantic import BaseModel, validator, Field, root_validator
from typing import Optional
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    SupplierEnum, 
    DataTypeEnum,
    CategoryEnum,
    SubCategoryEnum, 
    AddOnEnum,
    WheelAttributeEnum,
    TireAttributeEnum
)
from webweaver.webscraping.pipelines.pipeline_cleaner import PipelineCleaner
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier, 
    VariationType,
    Category,
    SubCategory
)
from webweaver.modules.project_modules.speed_fanatics.speed_validators import (
    TireAttributeValidator,
    WheelAttributeValidator,
    ProductValidator,
)
# class SupplierValidation(BaseModel):
#     supplier_enum: Supplier



class CategoriesValidation(BaseModel):
    category: Category
    subcategory: SubCategory

    class Config:
        arbitrary_types_allowed = True



class ProductValidation(BaseModel):

    # supplier: SupplierValidation
    product_name: str
    description: Optional[str]
    description_long: Optional[str] = Field(default=None)
    product_code: Optional[str] = Field(default=None)
    is_sale: bool = Field(default=False)

    _clean_str = validator('product_name', pre=True)(PipelineCleaner.clean_str)
    _clean_product_code = validator('product_code')(ProductValidator.clean_product_code)



class PriceValidation(BaseModel):

    msrp: Decimal
    is_old: bool = Field(default=False)

    _to_decimal = validator("msrp", pre=True)(PipelineCleaner.to_decimal_rounded)


class CostValidation(BaseModel):
    cost: Decimal

    _to_decimal = validator("cost", pre=True)(PipelineCleaner.to_decimal_rounded)


class VariationTypeValidation(BaseModel):
    variation_type_name: str
    data_type: DataTypeEnum = Field(default=DataTypeEnum.STRING)
    is_required: bool = Field(default=True)


class VariationValueValidation(BaseModel):
    value: str
    price_modifier: Optional[Decimal] = Field(default=None)

    _to_decimal = validator("price_modifier", pre=True)(PipelineCleaner.to_decimal_rounded_or_zero)


class ProductVariationValidation(BaseModel):
    variation_type: VariationTypeValidation
    variation_values: list[VariationValueValidation]


class AddOnValidation(BaseModel):
    add_on_enum: AddOnEnum
    name: str
    detail: Optional[str] = Field(default=None)
    price_modifier: Decimal = Field(default=None)

    _to_decimal = validator("price_modifier", pre=True)(PipelineCleaner.to_decimal_rounded_or_zero)


class ProductImageValidation(BaseModel):
    # product: ProductValidation
    image: Optional[bytes]

class ProductImageUrlValidation(BaseModel):
    image_url: str

    _is_url = validator('image_url')(PipelineCleaner.url_domain_dirs)


class WheelAttributeValidation(BaseModel):
    diameter : float
    width: float
    centerbore: Optional[float] = Field(default=None)
    bolt_pattern: Optional[str] = Field(default=None)
    finish: Optional[str] = Field(default=None)
    load_rating: Optional[float] = Field(default=None)
    weight: Optional[float] = Field(default=None)
    backspacing: Optional[float] = Field(default=None)
    lugs: Optional[int] = Field(default=None)
    offset: Optional[int] = Field(default=None)

    _to_float = validator('diameter','width', pre=True)(PipelineCleaner.to_float)
    _to_float_or_none = validator('centerbore','load_rating','weight','backspacing', pre=True)(PipelineCleaner.to_float_or_none)
    _offset = validator('offset', pre=True)(WheelAttributeValidator.offset)
    _bolt_pattern = validator('bolt_pattern')(WheelAttributeValidator.bolt_pattern)
    _load_rating = validator('load_rating', pre=True)(WheelAttributeValidator.load_rating)


class TireAttributeValidation(BaseModel):
    width: int
    wheel_diameter: int
    aspect_ratio: Optional[int] = Field(default=None)
    load_index: Optional[int] = Field(default=None)
    load_index_dual: Optional[int] = Field(default=None)
    speed_rating: Optional[str] = Field(default=None)
    load_description: Optional[str] = Field(default=None)
    utqg: Optional[str] = Field(default=None)
    overall_diameter: Optional[float] = Field(default=None)
    studdable: Optional[bool] = Field(default=None)
    service_type: Optional[str] = Field(default=None)

    _to_int_rounded = validator('width','wheel_diameter', pre=True)(PipelineCleaner.to_int_rounded)
    _to_int = validator('aspect_ratio','load_index','load_index_dual', pre=True)(PipelineCleaner.to_int_or_none)
    _to_float = validator('overall_diameter', pre=True)(PipelineCleaner.to_float_or_none)
    _utqg = validator('utqg', pre=True)(TireAttributeValidator.utqg)


class BrandValidation(BaseModel):
    brand_name: str



class ProductSpecValidation(BaseModel):
    weight: Optional[float] = Field(default=None)
    height: Optional[float] = Field(default=None)
    width: Optional[float] = Field(default=None)
    length: Optional[float] = Field(default=None)

    # @root_validator
    # def check_all_fields(cls, values):
    #     if not any(values.values()):
    #         raise ValueError("All fields are None")
    #     return values



# /End of reusable models
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


class SupplierAbstractModel(BaseModel):
    """When my pydantic models have merged into 1 UnifiedValidation model then I will incorporate
    this abstract class into all my supplier models for standardized validation.
    """
    ...
    # @root_validator(pre=True)
    # def wheel_or_tire(cls, values):
    #     """Checks to make sure we are not trying to pass WheelAttribute data and TireAttribute
    #     data at the same time. A product is a wheel, or a tire, or neither. If we are trying to
    #     send wheel and tire data together then there is a misconfiguration in the spider's code.
    #     """
    #     return values


class EssexPartsValidation(BaseModel):
    
    supplier: Supplier
    brand: BrandValidation
    categories: CategoriesValidation
    product: ProductValidation
    variations: Optional[list[ProductVariationValidation]]
    price: PriceValidation
    image_urls: list[ProductImageUrlValidation]
    # product_specs: Optional[ProductSpecValidation]


    class Config:
        arbitrary_types_allowed = True  # this is so we can have Supplier object as a value


class TheWheelShopValidation(BaseModel):
    supplier: Supplier
    brand: BrandValidation
    categories: CategoriesValidation
    tire_attributes: Optional[TireAttributeValidation] = Field(default=None)
    wheel_attributes: Optional[WheelAttributeValidation] = Field(default=None)
    product: ProductValidation
    prices: list[PriceValidation]
    image_urls: Optional[list[ProductImageUrlValidation]]

    # images: Optional[list[ProductImageValidation]]

    class Config:
        arbitrary_types_allowed = True


class VerusValidation(BaseModel):

    supplier: Supplier
    brand: BrandValidation
    product: ProductValidation
    price: PriceValidation
    images: list[ProductImageValidation]

    class Config:
        arbitrary_types_allowed = True


class SoulPPValidation(BaseModel):

    supplier: Supplier
    brand: BrandValidation
    product: ProductValidation
    prices: list[PriceValidation]
    variations: Optional[list[ProductVariationValidation]]
    add_ons: Optional[list[AddOnValidation]]
    images: Optional[list[ProductImageValidation]] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


class FastcoValidation(BaseModel):

    categories: CategoriesValidation
    supplier: Supplier
    brand: BrandValidation
    product: ProductValidation
    wheel_attributes: Optional[WheelAttributeValidation]
    tire_attributes: Optional[TireAttributeValidation]
    price: PriceValidation
    cost: CostValidation
    image_url: ProductImageUrlValidation

    class Config:
        arbitrary_types_allowed = True



class UnifiedValidation(BaseModel):
    """This will be the unified model of all supplier models.

    Once this is implemented, SpeedPipeline will only expect a single 
    data type: UnifiedValidation. From there it can figure out which
    type of supplier validation object its dealing with.
    """
    fastco: Optional[FastcoValidation] = Field(default=None)
    essex_parts: Optional[EssexPartsValidation] = Field(default=None)
    wheel_shop: Optional[TheWheelShopValidation] = Field(default=None)
    verus_engineering: Optional[VerusValidation] = Field(default=None)
    soul_pp: Optional[SoulPPValidation] = Field(default=None)


    @root_validator(pre=True)
    def ensure_one(cls, values):
        """Checks to make sure at least one of the values is not None."""
        if not any(values):
            raise ValueError("No data from any suppliers found")

        return values
