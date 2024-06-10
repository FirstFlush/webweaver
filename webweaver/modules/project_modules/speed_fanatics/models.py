from decimal import Decimal
import io
import os
from PIL import Image
from tortoise import Model, fields

from webweaver.webscraping.models import ScrapeModel
from webweaver.modules.project_modules.speed_fanatics.constants import SPEED_IMAGE_DIR
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum, 
    SubCategoryEnum,
    SupplierEnum, 
    AddOnEnum,
    DataTypeEnum,
    VehicleMakeEnum,
    CountryEnum
)


class Category(Model):
    # category_name   = fields.CharField(CategoryEnum, unique=True)
    category_name   = fields.CharEnumField(CategoryEnum, unique=True)
    pretty_name     = fields.CharField(max_length=255, unique=True, null=True)
    is_active       = fields.BooleanField(default=True)

    def __str__(self):
        return self.category_name.value


class SubCategory(Model):
    category            = fields.ForeignKeyField('models.Category', related_name='subcategories', on_delete=fields.CASCADE, null=True)
    subcategory_name    = fields.CharEnumField(SubCategoryEnum, unique=True)
    pretty_name         = fields.CharField(max_length=255, unique=True, null=True)
    is_active           = fields.BooleanField(default=True)

    def __str__(self):
        return self.subcategory_name.value


class Supplier(Model):

    supplier_name   = fields.CharEnumField(SupplierEnum, unique=True, max_length=255)
    spider_asset    = fields.OneToOneField('models.SpiderAsset', related_name='supplier', on_delete=fields.SET_NULL, null=True)
    is_active       = fields.BooleanField(default=True)
    # can_dropshop    = fields.BooleanField(default=False)
    country         = fields.CharEnumField(CountryEnum, max_length=255, default=CountryEnum.CANADA)
    date_created    = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def active_suppliers(cls, **kwargs) -> list["Supplier"]:
        return await cls.filter(is_active=True)

    @property
    def supplier_dir(self) -> str:
        """Returns the directory the supplier images would be saved in.
        #NOTE this works for now, but probably a more robust way to do this function?
        """
        return self.supplier_name.value.lower().replace(' ', '-')


class Brand(ScrapeModel):
    brand_name      = fields.CharField(max_length=255, unique=True)
    date_created    = fields.DatetimeField(auto_now_add=True)

    async def save(self, *args, **kwargs):
        self.brand_name = self.brand_name.strip()
        await super().save(*args, **kwargs)

    # @classmethod
    # async def get_or_create(cls, **kwargs):
    #     # need to pass in project handler to make this work. not ideal.
    #     await super().get_or_create(**kwargs)


class VehicleMake(ScrapeModel):
    vehicle_make = fields.CharField(max_length=255, unique=True)


class VehicleModel(ScrapeModel):
    vehicle_make    = fields.ForeignKeyField('models.VehicleMake', related_name='vehicle_models', on_delete=fields.CASCADE)
    vehicle_model   = fields.CharField(max_length=255)

    class Meta:
        unique_together = (('vehicle_make', 'vehicle_model'),)


class Product(ScrapeModel):

    category        = fields.ForeignKeyField('models.Category', related_name='products', on_delete=fields.CASCADE, default=10) # default UNKNOWN
    subcategory     = fields.ForeignKeyField('models.SubCategory', related_name='products', on_delete=fields.CASCADE, default=30) # default UNKNOWN
    brand           = fields.ForeignKeyField('models.Brand', related_name='products', on_delete=fields.CASCADE, null=True)
    supplier        = fields.ForeignKeyField('models.Supplier', related_name='products', on_delete=fields.CASCADE)
    product_name    = fields.CharField(max_length=255)
    product_code    = fields.CharField(max_length=255, null=True)
    description     = fields.TextField(null=True)
    description_long= fields.TextField(null=True)
    is_sale         = fields.BooleanField(default=False)
    is_active       = fields.BooleanField(default=True)
    is_special_order= fields.BooleanField(default=False)
    date_modified   = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product_name', 'supplier'),)

    async def get_msrp(self) -> Decimal:
        price = await Price.current_price(product=self)
        return price.msrp
    
    async def get_cost(self) -> Decimal:
        cost = await Cost.current_cost(product=self)
        return cost.cost

    @classmethod
    async def save(self, *args, **kwargs):
        self.product_name = self.product_name.strip()
        if self.description:
            self.description = self.description.strip()
        if self.description_long:
            self.description_long = self.description_long.strip()
        await super().save(*args, **kwargs)


class Cost(ScrapeModel):
    product         = fields.ForeignKeyField('models.Product', related_name='cost', on_delete=fields.CASCADE)
    cost            = fields.DecimalField(max_digits=16, decimal_places=2)
    date_modified   = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'cost'),)

    @classmethod
    async def current_cost(cls, product:Product) -> "Cost":
        cost = await cls.filter(product=product).order_by('-date_created').first()
        if not cost:
            raise ValueError(f"No cost objects found for product ID: {product.id}")
        return cost


class Price(ScrapeModel):

    product         = fields.ForeignKeyField('models.Product', related_name='prices', on_delete=fields.CASCADE)
    msrp            = fields.DecimalField(max_digits=16, decimal_places=2)
    is_old          = fields.BooleanField(default=False)
    date_modified   = fields.DatetimeField(auto_now=True)
    date_created    = fields.DatetimeField(auto_now_add=True)


    @classmethod
    async def current_price(cls, product:Product) -> "Price":
        """Retrieve the most current Price object"""
        price = await cls.filter(product=product, is_old=False).order_by('-date_created').first()
        if not price:
            raise ValueError(f"No prices found for product ID: {product.id}")
        return price


    class Meta:
        unique_together = (('product', 'msrp'),)


class VariationType(Model):
    data_type           = fields.CharEnumField(DataTypeEnum, default=DataTypeEnum.STRING)
    variation_type_name = fields.CharField(max_length=255, unique=True)
    is_required         = fields.BooleanField(default=True)
    date_created        = fields.DatetimeField(auto_now_add=True)


class ProductVariation(ScrapeModel):
    """The required_variations column attempts to map the relationship between variations that
    are dependent on other variations.

    For example: https://soulpp.com/product/porsche-718-gt4-rs-race-exhaust-package/
    For this exhaust package, the weissach tip finish is dependent on the user selecting
    the weissach tip style. However the matte-black and signature-satin finishes can
    be applied to either slash-cut or straight-cut tips, but they can not be applied to
    weissach-style tips. 
    
    An easy way to express this is to say: 
    1. weissach finish has weissach tip as a required variation
    2. matte-black and signature-satin have slash-cut & straight-cut as required variations.

    Any of the variations in the required_variations list will satisfy the constraint.
    """
    product             = fields.ForeignKeyField('models.Product', related_name='variations', on_delete=fields.CASCADE)
    variation_type      = fields.ForeignKeyField('models.VariationType', related_name='variations', on_delete=fields.CASCADE)
    value               = fields.CharField(max_length=255)
    price_modifier      = fields.DecimalField(max_digits=16, decimal_places=2, null=True)
    required_variations = fields.ManyToManyField('models.ProductVariation')
    date_modified       = fields.DatetimeField(auto_now=True)
    date_created        = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'variation_type', 'value'),)


    @classmethod
    async def get_variations_from_product(cls, product:Product):
        """This seems more relevant to the store-front than to scraping... lol"""
        await cls.filter(product=product).prefetch_related('variation_type')


# class VariationConstraint(ScrapeModel):
#     """This table attempts to map the relationship between variations that
#     are dependent on other variations.

#     For example: https://soulpp.com/product/porsche-718-gt4-rs-race-exhaust-package/
#     For this exhaust package, the weissach tip finish is dependent on the user selecting
#     the weissach tip style. However the matte-black and signature-satin finishes can
#     be applied to either slash-cut or straight-cut tips, but they can not be applied to
#     weissach-style tips. 
    
#     An easy way to express this is to say: 
#     1. weissach finish has weissach tip as a required variation
#     2. matte-black and signature-satin have slash-cut & straight-cut as required variations.

#     Any of the variations in the required_variations list will satisfy the constraint.
#     """
#     variation             = fields.OneToOneField('models.ProductVariation', related_name='constraints', on_delete=fields.CASCADE)
#     required_variations   = fields.ManyToManyField('models.ProductVariation', related_name='required_by')
#     # excluded_variations = fields.ManyToManyField('models.ProductVariation', related_name='excluded_by')
#     date_created          = fields.DatetimeField(auto_now_add=True)


class AddOn(ScrapeModel):
    """An AddOn is an extra purchase that can be made on top of the Product purchase. 
    This is different from a variation. A product can be purchased without an add-on,
    where as it can not be purchased without a variation.
    """
    product         = fields.ForeignKeyField('models.Product', related_name='add_ons', on_delete=fields.CASCADE)
    add_on_enum     = fields.CharEnumField(AddOnEnum, default=AddOnEnum.EXTRA_PURCHASE.value)
    name            = fields.CharField(max_length=255)
    detail          = fields.CharField(max_length=255, null=True)
    price_modifier  = fields.DecimalField(max_digits=16, decimal_places=2)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'name'),)


class WheelAttribute(ScrapeModel):
    product             = fields.OneToOneField('models.Product', related_name='wheel_attribute', on_delete=fields.CASCADE)
    diameter            = fields.FloatField() #in inches
    width               = fields.FloatField() #in inches
    centerbore          = fields.FloatField(null=True)
    bolt_pattern        = fields.CharField(max_length=255, null=True) # Also called PCD (Pitch Circle Diameter)
    finish              = fields.CharField(max_length=255, null=True)
    load_rating         = fields.FloatField(null=True) # kg
    weight              = fields.FloatField(null=True)
    backspacing         = fields.FloatField(null=True)
    offset              = fields.CharField(max_length=255, null=True)


class TireAttribute(ScrapeModel):
    """UTQG stands for Uniform Tire Quality Grade"""
    product             = fields.OneToOneField('models.Product', related_name='tire_attribute', on_delete=fields.CASCADE)
    width               = fields.SmallIntField()
    aspect_ratio        = fields.SmallIntField(null=True) # aka profile
    wheel_diameter      = fields.SmallIntField()
    load_index          = fields.SmallIntField(null=True)
    load_index_dual     = fields.SmallIntField(null=True)
    speed_rating        = fields.CharField(max_length=4, null=True)
    load_description    = fields.CharField(max_length=255, null=True)
    utqg                = fields.CharField(max_length=255, null=True)
    overall_diameter    = fields.FloatField(null=True)
    studdable           = fields.BooleanField(default=False, null=True)
    service_type        = fields.CharField(max_length=2, null=True)


class ProductImage(ScrapeModel):
    
    product         = fields.ForeignKeyField('models.Product', related_name='images', on_delete=fields.CASCADE)
    file_name       = fields.CharField(max_length=255)
    is_primary      = fields.BooleanField(default=False)
    is_image_sent   = fields.BooleanField(default=False)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'file_name'),)


    def save_image_file(self, binary_data:bytes, file_name:str):
        """Converts the binary data to JPEG and saves it as a file."""
        image = Image.open(io.BytesIO(binary_data))
        buffer = io.BytesIO()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffer, format='JPEG') # saves to in-memory buffer before saving to file.
        clean_binary_data = buffer.getvalue()
        with open(file_name, "wb") as file:
            file.write(clean_binary_data)



    @staticmethod
    def supplier_image_dir(supplier_enum:SupplierEnum) -> str:
        return supplier_enum.value.lower().replace(' ', '_')

    @classmethod
    def full_path(cls, supplier_enum:SupplierEnum, file_name:str, counter:int=None) -> str:
        """Returns the image's full path as a string"""
        if not counter:
            return os.path.join(SPEED_IMAGE_DIR, cls.supplier_image_dir(supplier_enum), file_name)
        else:
            return os.path.join(SPEED_IMAGE_DIR, cls.supplier_image_dir(supplier_enum), f"{file_name}_{counter}")

    @classmethod
    def create_file_name(cls, supplier_enum:SupplierEnum, product_name:str, ext:str='jpg') -> str:
        """Replace unwanted chars with str translation table and str.replace() and return
        the file name.
        """
        bad_chars = " :,&./\\"
        translaton_table = str.maketrans({char:'-' for char in bad_chars})
        file_name = product_name.lower().translate(translaton_table) \
            .replace("°", "deg")    \
            .replace('+','plus')
        full_path = cls.full_path(supplier_enum=supplier_enum, file_name=file_name)
        counter = 1
        while os.path.exists(f"{full_path}.{ext}"):
            counter += 1
            full_path = cls.full_path(
                supplier_enum=supplier_enum, 
                file_name=file_name,
                counter=counter,
            )
        return f"{full_path}.{ext}".replace(f"{SPEED_IMAGE_DIR}/", '')


class ProductImageUrl(ScrapeModel):
    """This table is for being sneaky lol.
    
    With certain suppliers, in order to scrape the products we must be logged in. 
    However image-scraping is requires a lot of extra HTTP requests. This table 
    exists so that we can scrape products while logged-in, capture the image URL, 
    and then scrape the image later, anonymously. Of course, this depends on the 
    web server allowing you to view the images without authenticating. 
    
    Really cool thing though is that seems to be a common misconfiguration lol.
    """
    product         = fields.ForeignKeyField('models.Product', related_name='image_urls', on_delete=fields.CASCADE)
    image_url       = fields.CharField(max_length=2048)
    image_scraped   = fields.BooleanField(default=False)
    date_created    = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (('product', 'image_url'),)


class ProductSpec(ScrapeModel):
        product = fields.OneToOneField('models.Product', related_name='product_specs', on_delete=fields.CASCADE)
        weight  = fields.FloatField(null=True)
        length  = fields.FloatField(null=True)
        width   = fields.FloatField(null=True)
        height  = fields.FloatField(null=True)

        async def save(self, *args, **kwargs):
            if any([self.weight, self.length, self.width, self.height]):
                super().save(*args, **kwargs)

