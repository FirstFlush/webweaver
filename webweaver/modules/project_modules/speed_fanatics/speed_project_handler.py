import logging

from webweaver.modules.project_modules.speed_fanatics.speed_pipeline import SpeedPipeline
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    SupplierEnum, 
    CategoryEnum, 
    SubCategoryEnum,
    DataTypeEnum
)
from webweaver.modules.project_modules.speed_fanatics.speed_fuzz import SpeedFuzzyHandler
from webweaver.modules.project_modules.speed_fanatics.models import (
    Supplier, 
    VariationType,
    Category,
    SubCategory,
    Brand,
    VehicleMake,
    VehicleModel,
)
from webweaver.modules.project_modules.speed_fanatics.categorization import (
    BrandHandler,
    CategoryHandler,
    SubCategoryHandler,
    VehicleHandler,
    SpecHandler
)
from webweaver.modules.project_modules.speed_fanatics.product_attributes.attribute_handler import AttributeHandler
from webweaver.modules.project_modules.speed_fanatics.speed_keywords import SpeedKeyWords
from webweaver.modules.project_modules.speed_fanatics.speed_mappings import SpeedMapping
from webweaver.modules.project_modules.speed_fanatics.speed_regex import SpeedRegex
# from webweaver.modules.project_modules.speed_fanatics.categorization.brand_handler import BrandHandler
from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.pipelines.pipeline_base import Pipeline 
from webweaver.webscraping.registry.scraping_registry import scraping_registry
from webweaver.project.project_base import ProjectHandler


logger = logging.getLogger('scraping')


class ProjectHandlerInterface:

    def __init__(self, project_handler:"SpeedProjectHandler"):
        self.project_handler:"SpeedProjectHandler" = project_handler


class SpeedProjectHandler(ProjectHandler):
    """NOTE Singleton pattern is in use here."""
    _instance = None
    interface:ProjectHandlerInterface = None
    pipeline_class:SpeedPipeline = None

    # mappings
    spider_asset_to_supplier:dict[SpiderAsset, Supplier] = {}
    brand_name_to_brand:dict[str, Brand] = {}
    category_enum_to_category:dict[CategoryEnum, Category] = {}
    subcategory_enum_to_subcategory:dict[SubCategoryEnum, SubCategory] = {}
    data_type_to_variation_type:dict[DataTypeEnum, VariationType] = {}
    vehicle_model_mapping = dict[str, VehicleModel]

    supplier_enum = SupplierEnum
    regex = SpeedRegex
    category_enum = CategoryEnum

    attribute_handler = AttributeHandler
    brand_handler = None
    category_handler = None
    spec_handler = None
    subcategory_handler = None
    fuzzy_handler = SpeedFuzzyHandler
    mapping = SpeedMapping
    keywords = SpeedKeyWords

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    

    async def initialize_project(self):
        self.interface = ProjectHandlerInterface(project_handler=self)
        self.pipeline_class = SpeedPipeline
        self.brand_handler = BrandHandler(self)
        self.category_handler = CategoryHandler(self)
        self.subcategory_handler = SubCategoryHandler(self)
        self.spec_handler = SpecHandler(self)
        self.vehicle_handler = VehicleHandler(self)
        await self._populate_spider_asset_mapping()
        await self._populate_category_mapping()
        await self._populate_subcategory_mapping()
        await self._populate_brand_mapping()
        await self._populate_vehicle_mapping()
        # await self._populate_variation_type_mapping()


    async def _populate_vehicle_mapping(self):
        ...


    async def _populate_brand_mapping(self):
        """Maps the following:
            brandname : Brand
        """
        brands = await Brand.all()
        for brand in brands:
            brand_name_text = self.brand_handler.normalize_brand_name(brand.brand_name)
            fuzzy_brand_name = self.fuzzy_handler.preprocess(brand_name_text)
            self.brand_name_to_brand[fuzzy_brand_name] = brand


    async def _populate_category_mapping(self):
        """Maps the following:
            CategoryEnum : Category
        """
        categories = await Category.filter(is_active=True)
        for category in categories:
            self.category_enum_to_category[category.category_name] = category


    async def _populate_subcategory_mapping(self):
        """Maps the following:
            SubCategoryEnum : SubCategory
        """
        subcategories = await SubCategory.filter(is_active=True)
        for subcategory in subcategories:
            self.subcategory_enum_to_subcategory[subcategory.subcategory_name] = subcategory


    async def _populate_spider_asset_mapping(self):
        """Maps the following model objects:
            SpiderAsset : Supplier
        """
        for spider_asset in scraping_registry.spiders:
            supplier = await Supplier.get_or_none(spider_asset=spider_asset)
            if not supplier:
                raise TypeError(f"no Supplier object pointing to {spider_asset.spider_name}!")
            self.spider_asset_to_supplier[spider_asset] = supplier


    # async def _populate_variation_type_mapping(self):
    #     """maps DataTypeEnum to VariationType for quick-access to 
    #     VariationType when saving a ProductVariation, without having to
    #     make a DB query to grab the VariationType and check its enum.
    #     """
    #     variation_types = await VariationType.all()
    #     for variation_type in variation_types:
    #         self.data_type_to_variation_type[variation_type.data_type] = variation_type
