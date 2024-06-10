import logging
from pydantic import BaseModel
from typing import TYPE_CHECKING

from tortoise.exceptions import IntegrityError, TransactionManagementError
from tortoise.transactions import in_transaction
from webweaver.webscraping.pipelines.pipeline_base import Pipeline
from webweaver.exceptions import PipelineError
from webweaver.webscraping.registry.scraping_registry import scraping_registry
from webweaver.modules.project_modules.speed_fanatics.constants import MIN_PRICE
from webweaver.modules.project_modules.speed_fanatics.speed_enums import SupplierEnum, CategoryEnum, DataTypeEnum
from webweaver.modules.project_modules.speed_fanatics.speed_validation import (
    EssexPartsValidation, 
    TheWheelShopValidation,
    VerusValidation,
    SoulPPValidation,
    FastcoValidation,
)
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier,
    Cost,
    Brand,
    Product,
    Price,
    ProductImage,
    TireAttribute,
    WheelAttribute,
    ProductVariation,
    VariationType,
    AddOn,
    ProductImageUrl
)

if TYPE_CHECKING:
    from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler


logger = logging.getLogger('scraping')


class SpeedPipeline(Pipeline):

    _schema = None
    # schema = EssexPartsValidation
    # schema = TheWheelShopValidation
    # schema = VerusValidation
    # schema = SoulPPValidation
    schema = FastcoValidation

    def get_supplier_enum(self, data_to_save:EssexPartsValidation=None) -> SupplierEnum:
        # NOTE  data_to_save is any speed validation model and will be changed once
        #       i have created the unified model for all suppliers
        if not data_to_save:
            raise ValueError(f"data_to_save is of type: `{type(data_to_save)}`")
        return data_to_save.supplier.supplier_name


    async def save_data(self):

        self.project_handler:"SpeedProjectHandler"
        data_to_save:EssexPartsValidation = self.data_to_save #this line is superfluous and the result of refactoring.

        try:
            supplier:Supplier = data_to_save.supplier
        except AttributeError as e:
            raise e


        match supplier.supplier_name:
            case SupplierEnum.ESSEX_PARTS:
                await self.save_essex_parts(data_to_save, supplier)
            case SupplierEnum.THE_WHEEL_SHOP:
                await self.save_wheel_shop(data_to_save, supplier)
            case SupplierEnum.SOUL_PP:
                await self.save_soul_pp(data_to_save, supplier)
            case SupplierEnum.VERUS_ENGINEERING:
                await self.save_verus(data_to_save, supplier)
            case SupplierEnum.FASTCO:
                await self.save_fastco(data_to_save, supplier)
            case _:
                msg = f"Invalid SupplierEnum of {supplier.supplier_name} for spider '{self.spider_asset.spider_name}'"
                raise PipelineError(msg)



    async def save_fastco(self, data_to_save:FastcoValidation, supplier:Supplier):

        # tire_attrs = data_to_save.tire_attributes.model_dump()
        # for key, value in data_to_save.model_dump().items():
        #     if key != 'categories':
        #         print(key, " : ", value)
        #     else:
        #         for key2, value2 in value.items():
        #             print("\t", key2, " : ", value2.__str__())

        async with in_transaction():

            categories = data_to_save.categories.model_dump()

            brand_tuple = await self.project_handler.brand_handler.get_or_create_brand(data_to_save.brand.brand_name)
            brand = brand_tuple[0]

            product_name = data_to_save.product.product_name

            product, created, updated = await Product.get_create_or_update(
                # **data_to_save.product.model_dump(), 
                supplier=supplier, 
                brand=brand,
                product_name=product_name,
                category=categories.get('category'),
                subcategory=categories.get('subcategory')
            )
            print('product id: ', product.id)

            if not created:
                for field_name, field_value in data_to_save.product.model_dump().items():
                    if getattr(product, field_name, None) != field_value:
                        setattr(product, field_name, field_value)
                await product.save()


            await Price.get_create_or_update(**data_to_save.price.model_dump(), product=product)

            await Cost.get_create_or_update(**data_to_save.cost.model_dump(), product=product)
            # await Cost.get_or_create(**data_to_save.cost.model_dump(), product=product)
            
            if data_to_save.tire_attributes:
                await TireAttribute.get_create_or_update(**data_to_save.tire_attributes.model_dump(), product=product)
            elif data_to_save.wheel_attributes:
                await WheelAttribute.get_create_or_update(**data_to_save.wheel_attributes.model_dump(), product=product)
            await ProductImageUrl.get_create_or_update(**data_to_save.image_url.model_dump(), product=product)

            # print("SAVED:")
            # print(product.product_name)
            # print(categories.get('category'))
            # print(categories.get('subcategory'))
            # print()
            # print()


    async def save_soul_pp(self, data_to_save:SoulPPValidation, supplier:Supplier):
        
        for key, value in data_to_save.model_dump().items():
            if key != 'images':
                print(key, " : ", value)
    
        async with in_transaction():
            brand_tuple = await Brand.get_or_create(**data_to_save.brand.model_dump())
            brand = brand_tuple[0]

            product_tuple = await Product.get_or_create(**data_to_save.product.model_dump(), supplier=supplier, brand=brand)
            product = product_tuple[0]

            for price in data_to_save.prices:
                await Price.get_or_create(**price.model_dump(), product=product)

            for variation in data_to_save.variations:
                variation_type_tuple = await VariationType.get_or_create(**variation.variation_type.model_dump())
                for variation_value in variation.variation_values:
                    await ProductVariation.get_or_create(
                        product=product, 
                        variation_type=variation_type_tuple[0], 
                        **variation_value.model_dump()
                    )

            for add_on in data_to_save.add_ons:
                await AddOn.get_or_create(**add_on.model_dump(), product=product)

            img_counter = 1
            for image in data_to_save.images:
                file_name = ProductImage.create_file_name(product.product_name, counter=img_counter)                
                image_tuple = await ProductImage.get_or_create(product=product, file_name=file_name)
                image_instance = image_tuple[0]
                if image_tuple[1]:
                    image_instance.save_image_file(
                        binary_data=image.image, 
                        supplier_enum=self.get_supplier_enum(data_to_save)
                    )
                img_counter += 1
            print("...SAVED")


    async def save_verus(self, data_to_save:VerusValidation, supplier:Supplier):
        """Logic for saving data scraped from VerusEngineering."""

        for key, value in data_to_save.model_dump().items():
            if key != 'images':
                print(key, " : ", value)

        async with in_transaction():
            brand_tuple = await Brand.get_or_create(**data_to_save.brand.model_dump())
            brand = brand_tuple[0]

            product_tuple = await Product.get_or_create(**data_to_save.product.model_dump(), supplier=supplier, brand=brand)
            product = product_tuple[0]

            price_tuple = await Price.get_or_create(**data_to_save.price.model_dump(), product=product)
            price = price_tuple[0]

            img_counter = 1
            for image in data_to_save.images:
                file_name = ProductImage.create_file_name(product.product_name, counter=img_counter)                
                image_tuple = await ProductImage.get_or_create(product=product, file_name=file_name)
                image_instance = image_tuple[0]
                if image_tuple[1]:
                    image_instance.save_image_file(
                        binary_data=image.image, 
                        supplier_enum=self.get_supplier_enum(data_to_save)
                    )
                img_counter += 1
            print("...SAVED")



    async def save_wheel_shop(self, data_to_save:TheWheelShopValidation, supplier:Supplier):
        """Logic for saving data scraped from the dreaded TheWheelShop."""

        # for key, value in data_to_save.model_dump().items():
        #     if key != 'images':
        #         print(key, " : ", value)

        async with in_transaction():

            category = data_to_save.categories.category
            subcategory = data_to_save.categories.subcategory
            brand, _ = await self.project_handler.brand_handler.get_or_create_brand(data_to_save.brand.brand_name)
            
            product, _, _ = await Product.get_create_or_update(
                **data_to_save.product.model_dump(), 
                supplier=supplier, 
                brand=brand,
                category=category,
                subcategory=subcategory,
            )


            for price in data_to_save.prices:
                await Price.get_create_or_update(**price.model_dump(), product=product)

            if data_to_save.wheel_attributes:
                await WheelAttribute.get_create_or_update(**data_to_save.wheel_attributes.model_dump(), product=product)
            elif data_to_save.tire_attributes:
                await TireAttribute.get_create_or_update(**data_to_save.tire_attributes.model_dump(), product=product)


            # ugly bit, change it when implement ProductAttribute
            # if data_to_save.attributes:
            #     if data_to_save.categories.category.category_enum == CategoryEnum.WHEELS:
            #         model_dict = {}
            #         for wheel_attribute in data_to_save.attributes:

            #             if wheel_attribute['attribute_type'].lower() == 'size':
            #                 wheel_attribute['attribute_type'] = 'wheel_size'

            #             model_dict[wheel_attribute['attribute_type'].lower().replace(' ','_')] = wheel_attribute['attribute_value']
                                        
            #         await WheelAttribute.get_create_or_update(product=product, **model_dict)

            #     elif data_to_save.categories.category.category_enum == CategoryEnum.TIRES:
            #         model_dict = {}
            #         for tire_attribute in data_to_save.attributes:
            #             if tire_attribute['attribute_type'].lower() == 'profile':
            #                 tire_attribute['attribute_type'] = 'aspect ratio'



            #             model_dict[tire_attribute['attribute_type'].lower().replace(' ','_')] = tire_attribute['attribute_value']

            #         await TireAttribute.get_create_or_update(product=product, **model_dict)

            for image_url in data_to_save.image_urls:
                # print('url to save: ', image_url)
                await ProductImageUrl.get_create_or_update(**image_url.model_dump(), product=product)
     

            # img_counter = 1
            # for image in data_to_save.images:
            #     file_name = ProductImage.create_file_name(product.product_name, counter=img_counter)                
            #     image_tuple = await ProductImage.get_create_or_update(product=product, file_name=file_name)
            #     image_instance = image_tuple[0]
            #     if image_tuple[1]:
            #         image_instance.save_image_file(
            #             binary_data=image.image, 
            #             supplier_enum=self.get_supplier_enum(data_to_save)
            #         )
            #     img_counter += 1
            print(product.product_name)
            print("...SAVED")
            print()



    async def save_essex_parts(self, data_to_save:EssexPartsValidation, supplier:Supplier):
        """Logic for saving data scraped from Essex Parts."""

        if data_to_save.price.msrp >= MIN_PRICE:
            async with in_transaction():
                category = data_to_save.categories.category
                subcategory = data_to_save.categories.subcategory

                brand, _ = await self.project_handler.brand_handler.get_or_create_brand(data_to_save.brand.brand_name)

                product, _, _ = await Product.get_create_or_update(
                    **data_to_save.product.model_dump(), 
                    supplier=supplier, 
                    brand=brand,
                    category=category,
                    subcategory=subcategory,
                )

                await Price.get_create_or_update(**data_to_save.price.model_dump(), product=product)
                if data_to_save.variations:
                    for variation in data_to_save.variations:
                        variation_type, _ = await VariationType.get_or_create(
                            variation_type_name=variation.variation_type.variation_type_name,
                            is_required = variation.variation_type.is_required
                        )
                        for variation_value in variation.variation_values:
                            await ProductVariation.get_create_or_update(
                                **variation_value.model_dump(),
                                variation_type = variation_type,
                                product = product
                            )
                for image_url in data_to_save.image_urls:
                    # print('url to save: ', image_url)
                    await ProductImageUrl.get_create_or_update(**image_url.model_dump(), product=product)
                # cost, _ = await Cost.get_or_create(**data_to_save.cost.model_dump(), product=product)
                # img_counter = 1
                # for image in data_to_save.images:
                #     file_name = ProductImage.create_file_name(product.product_name, counter=img_counter)                
                #     image_tuple = await ProductImage.get_or_create(product=product, file_name=file_name)
                #     image_instance = image_tuple[0]
                #     if image_tuple[1]:
                #         image_instance.save_image_file(
                #             binary_data=image.image, 
                #             supplier_enum=self.get_supplier_enum(data_to_save)
                #         )
                #     img_counter += 1

                # print('[SAVED] ', product.product_name)
                # print()
                # product_image_dict = data_to_save.product_image.model_dump()
                # image:bytes = product_image_dict.get('image')
                # if image:
                #     file_name = ProductImage.create_file_name(product.product_name)
                #     product_image_tuple = await ProductImage.get_or_create(
                #         product = product,
                #         file_name = file_name
                #     )
                #     # save teh image to a file
                #     product_image = product_image_tuple[0]
                #     if product_image_tuple[1]:
                #         product_image.save_image_file(
                #             binary_data=image, 
                #             supplier_enum=self.get_supplier_enum(data_to_save)
                #         )
                        
                # print('='*50)
                # print(f">> Saved:  {product.product_name}")
                # print(f">>$ {price.msrp}")
                # if product.description:
                #     print(f">> {product.description[:80]}")
                # if image:
                #     print(product_image)
                # if product_image_tuple[1]:
                #     print('Newly created image')
                # print()
        else:
            print(f"Skipping product: {data_to_save.product.product_name}")
            print(f"price of ${data_to_save.price.msrp} too low, skipping")
            print()



    def print_data(self, data_to_save:BaseModel):
        """For testing purposes, if we want to print the scraped 
        and cleaned data instead of save it.

        *Does not print image binary data
        *Very ugly but it works.
        """
        for key, value in data_to_save.model_dump().items():
            if key == 'image':
                print(key, ' : ', 1)
            elif key == 'images':
                print(len(value))
            else:
                if isinstance(value, BaseModel):
                    print(key, ' : ')
                    for key2, value2 in value.model_dump().items():
                        if key2 == 'image':
                            print('\t', key2, ' : ', bool(value2))
                        else:
                            print('\t', key2, ' : ', value2)
                elif isinstance(value, dict):
                    print(key, ' : ')
                    for key2, value2 in value.items():
                        if key2 == 'image':
                            print('\t', key2, ' : ', bool(value2))
                        else:
                            print('\t', key2, ' : ', value2)
                else:
                    print(key, ' : ', value)

        print()
        print()




    # async def get_or_create_brand(self, brand_name:str) -> Brand:
    #     """Check the brand mapping to see if we already have an instance of this brand.
    #     If the brand already exists, return it. If not, create a new brand.
    #     """
    #     brand_name_fuzzy = self.project_handler.fuzzy_handler.preprocess(brand_name)
    #     brand = self.project_handler.brand_name_to_brand.get(brand_name_fuzzy)
    #     if not brand:
    #         brand_stripped = self._brand_keyword_check(brand_name_fuzzy)


    #         if not brand:
    #             brand = await Brand.create(brand_name=brand_name)
    #     return brand



    # def _brand_keyword_check(self, brand_name:str) -> Brand | None:
    #     """If the brand name is not an exact match in our DB then
    #     we apply an additional step of stripping out particular
    #     key words, then matching again. 

    #     This will catch "Pirelli Tires" if it's saved in the DB
    #     as "Pirelli", but it will not catch "Pirelli" if we have
    #     "Pirelli Tires" in our DB.
    #     """
    #     self.project_handler.keywords.remove_brand_keywords(brand_name)


