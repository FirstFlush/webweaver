from collections import defaultdict
from pprint import pprint

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any, Type
from webweaver.config import TEMPLATES, templates

from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    DataTypeEnum,
    SupplierEnum,
)
from webweaver.modules.project_modules.speed_fanatics.models import (
    Product,
    ProductVariation, 
    AddOn,
    Price,
    WheelAttribute,
    TireAttribute,
    Supplier,
    Brand,
    ProductImage,
)


router = APIRouter()



@router.get("/mapping")
async def generate_attribute_map():

    wheel_attributes = await WheelAttribute.all()

    # Initialize a nested dictionary
    attribute_mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for attribute in wheel_attributes:
        # For each attribute, add its values to the mapping
        # Assuming attribute has fields like wheel_size, centerbore, etc.
        attribute_mapping["wheel_sizes"][attribute.wheel_size]["centerbores"].append(attribute.centerbore)
        attribute_mapping["wheel_sizes"][attribute.wheel_size]["bolt_patterns"].append(attribute.bolt_pattern)
        # ... and so on for other fields

        attribute_mapping["centerbores"][attribute.centerbore]["wheel_sizes"].append(attribute.wheel_size)
        
        # ... and so on for other fields

    # Remove duplicates and convert defaultdict to regular dict for easier use
    for main_attr, sub_attrs in attribute_mapping.items():
        for sub_attr, values in sub_attrs.items():
            attribute_mapping[main_attr][sub_attr] = {k: list(set(v)) for k, v in values.items()}
    attribute_mapping = dict(attribute_mapping)

    def convert_defaultdict(d):
        if isinstance(d, defaultdict):
            # Convert the defaultdict itself
            d = dict(d)
        for key, value in d.items():
            if isinstance(value, defaultdict):
                # Recursively convert nested defaultdicts
                d[key] = convert_defaultdict(value)
        return d

    # Use this function to convert your structure
    converted_structure = convert_defaultdict(attribute_mapping)

    print('=======================================')
    print()
    pprint(converted_structure)
    print()


def _attributes_dict_from_object(product_attribute:WheelAttribute|TireAttribute) -> dict[str, Any]:
    """Create the attribute dict for wheel/tire attribute objects."""
    nono_keys = {'product_id', 'scrape_job_id_id', 'id'}
    d = {}
    for key, value in product_attribute.__dict__.items():
        if key in nono_keys or key.startswith('_'):
            continue
        d[key] = value
    return d       


def _attributes_from_class(product_attribute_class:Type[WheelAttribute] | Type[TireAttribute]) -> list[str]:
    """Create the attribute dict for wheel/tire attribute objects."""
    nono_keys = {'product_id', 'scrape_job_id_id', 'id', 'product', 'scrape_job_id'}
    cols = []
    for column in product_attribute_class._meta.fields:
        if column in nono_keys or column.startswith('_'):
            continue
        cols.append(column)
    return cols





@router.get("/search/{product_type}")
# @router.get(ROUTES.SPEED_FANATICS_SEARCH)
async def search(request:Request, product_type:str):

    params = request.query_params
    found_wheels = None
    found_tires = None
    query_attributes = {}


    if product_type == 'wheels':
        attributes = _attributes_from_class(WheelAttribute)
        for attribute in attributes:
            for param_key, param_value in params.items():
                if param_key == attribute and param_value:
                    query_attributes[attribute] = param_value

        found_wheel_attributes = await WheelAttribute.filter(**query_attributes).prefetch_related('product')
        found_wheels = [wheel_attribute.product for wheel_attribute in found_wheel_attributes]

    elif product_type == 'tires':
        attributes = _attributes_from_class(TireAttribute)
        for attribute in attributes:
            for param_key, param_value in params.items():
                if param_key == attribute and param_value:
                    query_attributes[attribute] = param_value
        found_tire_attributes = await TireAttribute.filter(**query_attributes).prefetch_related('product')
        found_tires = [tire_attribute.product for tire_attribute in found_tire_attributes]

    else:
        return {'stop':'fucking around'}

    products = await Product.all().prefetch_related('brand', 'supplier')
    products.reverse()



    wheel_cols = _attributes_from_class(WheelAttribute)
    tire_cols = _attributes_from_class(TireAttribute)

    wheel_attributes = await WheelAttribute.all()
    tire_attributes = await TireAttribute.all()

    distinct_wheel_attribute_values = {}
    for column in wheel_cols:
        distinct_attrs = list({getattr(wa, column) for wa in wheel_attributes if getattr(wa, column)})
        distinct_wheel_attribute_values[column] = distinct_attrs
        distinct_wheel_attribute_values[column].sort()


    distinct_tire_attribute_values = {}
    for column in tire_cols:
        distinct_attrs = list({getattr(ta, column) for ta in tire_attributes if getattr(ta, column)})
        distinct_tire_attribute_values[column] = distinct_attrs
        distinct_tire_attribute_values[column].sort()

    context = {
        'products' : products,
        'found_wheels': found_wheels,
        'found_tires': found_tires,
        'query': query_attributes,
        'wheel_values': distinct_wheel_attribute_values,
        'tire_values': distinct_tire_attribute_values,
    }


    return templates.TemplateResponse(TEMPLATES.SPEED_FANATICS_PRODUCTS, {'request':request, **context})




@router.get("/products")
async def products(request: Request):

    products = await Product.all().prefetch_related('brand', 'supplier')
    products.reverse()

    wheel_cols = _attributes_from_class(WheelAttribute)
    tire_cols = _attributes_from_class(TireAttribute)

    wheel_attributes = await WheelAttribute.all()
    tire_attributes = await TireAttribute.all()

    distinct_wheel_attribute_values = {}
    for column in wheel_cols:
        distinct_attrs = list({getattr(wa, column) for wa in wheel_attributes if getattr(wa, column)})
        distinct_wheel_attribute_values[column] = distinct_attrs
        distinct_wheel_attribute_values[column].sort()

    distinct_tire_attribute_values = {}
    for column in tire_cols:
        distinct_attrs = list({getattr(ta, column) for ta in tire_attributes if getattr(ta, column)})
        distinct_tire_attribute_values[column] = distinct_attrs
        distinct_tire_attribute_values[column].sort()

    context = {
        'products': products,
        'wheel_values': distinct_wheel_attribute_values,
        'tire_values': distinct_tire_attribute_values,
    }

    return templates.TemplateResponse(TEMPLATES.SPEED_FANATICS_PRODUCTS, {'request':request, **context})


@router.get("/products/{product_id}")
async def pdp(request: Request, product_id:int):
    product = await Product.get(id=product_id).prefetch_related('brand', 'supplier', 'variations','add_ons')
    prices = await Price.filter(product=product)
    wheel_attribute = await WheelAttribute.get_or_none(product=product)
    tire_attribute = await TireAttribute.get_or_none(product=product)
    images = await ProductImage.filter(product=product)

    variations = await ProductVariation.filter(product=product).prefetch_related('variation_type')
    add_ons = await AddOn.filter(product=product)

    if tire_attribute:
        tire_attribute.attributes = _attributes_dict_from_object(tire_attribute)

    if wheel_attribute:
        wheel_attribute.attributes = _attributes_dict_from_object(wheel_attribute)

    for image in images:
        image.src = image.full_path(supplier_enum=product.supplier.supplier_enum)
        
    context = {
        'product'           : product,
        'wheel_attribute'   : wheel_attribute,
        'tire_attribute'    : tire_attribute,
        'images'            : images,
        'prices'            : prices,
        'variations'        : variations,
        'add_ons'           : add_ons,
    }
    return templates.TemplateResponse(TEMPLATES.SPEED_FANATICS_PDP, {'request':request, **context})