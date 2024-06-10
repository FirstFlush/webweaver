from enum import Enum


class CountryEnum(Enum):
    CANADA = 'CAN'
    UNITED_STATES = 'USA'


class SupplierEnum(Enum):
    """Suppliers for products"""
    ESSEX_PARTS = 'Essex Parts'
    VERUS_ENGINEERING = 'Verus Engineering'
    SOUL_PP = 'Soulpp'
    THE_WHEEL_SHOP = 'The Wheel Shop'

    FASTCO = 'Fastco'
    LN_ENGINEERING = 'LN Engineering'
    MCGILL_MOTORSPORT = 'McGill Motorsport'


class CategoryEnum(Enum):
    AUTOBODY = 'Autobody'
    BRAKES = 'Brakes'
    EXHAUST = 'Exhaust'
    INTAKE = 'Intake'
    RACEWEAR = 'Racewear'
    SUSPENSION = 'Suspension'
    TIRES = 'Tires'
    TIRE_ACCESSORIES = 'Tire Accessories'
    WHEELS = 'Wheels'
    WHEEL_ACCESSORIES = 'Wheel Accessories'
    UNKNOWN = 'Unknown'


class SubCategoryEnum(Enum):

    #Autobody
    BODY_KITS = 'Body Kits'
    SPOILERS = 'Spoilers'
    DIFFUSERS = 'Diffusers'
    AUTOBODY_MISC = 'Autobody Misc'
    #Brakes
    BRAKE_BUNDLES = 'Brake Bundles' # pads, lines, fluid, discs that work with OEM calipers
    BRAKE_CALIPERS = 'Brake Calipers'
    BRAKE_DISCS = 'Brake Discs'
    BRAKE_FLUIDS = 'Brake Fluids'
    BRAKE_KITS = 'Brake Kits'
    BRAKE_LINES = 'Brake Lines'
    BRAKE_PADS = 'Brake Pads'
    MASTER_CYLINDERS = 'Master Cylinders'
    #Exhaust
    EXHAUST_SYSTEMS = 'Exhaust Systems'
    #Intake
    AIR_FILTERS = 'Air Filters'
    #Racewear
    SUITS = 'Suits'
    BOOTS = 'Boots'
    GLOVES = 'Gloves'
    HELMETS = 'Helmets'
    CLOTHING = 'Clothing'
    #Suspension
    BAR_BUSHINGS = 'Bar Bushings'
    SHOCK_ABSORBERS = 'Shock Absorbers'
    SPRINGS = 'Springs'
    STRUTS = 'Struts'
    SWAY_BARS = 'Sway Bars'
    #Tires
    TIRES_SUMMER = 'Summer Tires' 
    TIRES_WINTER = 'Winter Tires'
    TIRES_ALL_SEASON = 'All-Season Tires'
    TIRES_ALL_WEATHER = 'All-Weather Tires'
    TIRES_ALL_TERRAIN = 'All-Terrain Tires'
    TIRES_MUD = 'Mud Tires'
    #Tire Accessories
    TIRES_MISC = 'Tire Misc'
    TIRES_STUDS = 'Tire Studs'
    TIRES_VALVES = 'Tire Valves'
    TPMS = 'TPMS'
    #Wheels
    WHEELS_AUTOMOTIVE = 'Wheels - Automotive'
    WHEELS_UTV_ATV = 'Wheels - UTV/ATV'
    #Wheel Accessories
    WHEEL_HUB_RINGS = 'Hub Rings'
    WHEEL_SPACERS = 'Wheel Spacers'
    WHEEL_ADAPTERS = 'Wheel Adapters'
    WHEEL_MISC = 'Wheel Misc'
    WHEEL_NUTS_BOLTS = 'Nuts & Bolts'
    WHEEL_CAPS = 'Wheel Caps'
    WHEEL_RIVETS = 'Wheel Rivets'
    #Unknown
    UNKNOWN = 'Unknown'


class DataTypeEnum(Enum):

    INTEGER = 'integer'
    STRING = 'string'
    FLOAT = 'float'
    UNKNOWN = 'unknown'


class MatchMode(Enum):
    """Used by category/subcategory handlers"""
    KEYWORDS = 'keywords'
    SUBSTRINGS = 'substrings'
    REGEX = 'regex'


class AttributeEnum(Enum):
    """Abstract base class for the various product attribute Enums.
    No plans for this yet
    """
    ...



class TireAttributeEnum(AttributeEnum):
    # PRODUCT = 'product'
    TIRE_WIDTH = 'width'
    ASPECT_RATIO = 'aspect_ratio'
    WHEEL_DIAMETER = 'wheel_diameter'
    LOAD_INDEX = 'load_index'
    LOAD_INDEX_DUAL = 'load_index_dual'
    SPEED_RATING = 'speed_rating'
    LOAD_DESCRIPTION = 'load_description'
    UTQG = 'utqg'
    OVERALL_DIAMETER = 'overall_diameter'
    STUDDABLE = 'studdable'
    SERVICE_TYPE = 'service_type'


class WheelAttributeEnum(AttributeEnum):
    # PRODUCT = 'product'     
    WHEEL_SIZE = 'wheel_size' # this is not in the model, but is used  to determine DIAMETER & WIDTH.
    DIAMETER = 'diameter'
    WIDTH = 'width'
    CENTERBORE = 'centerbore'
    OFFSET = 'offset'
    BOLT_PATTERN = 'bolt_pattern'
    FINISH = 'finish'
    WEIGHT = 'weight'
    LOAD_RATING = 'load_rating'
    BACKSPACING = 'backspacing'
    LUGS = 'lugs'



class EssexPartsCategoryEnum(Enum):
    """so far these are just a bunch of categories as seen on various websites.
    These will be converted into a unified schema with CategoryEnum & SubCategoryEnum.

    *One Product might be a part of multiple subcategories
    """
    ACCESSORIES = 'accessories'
    BRAKE_BUNDLES = 'brake_bundles' # pads, lines, fluid, discs that work with OEM calipers
    BRAKE_CALIPERS = 'brake_calipers'
    BRAKE_DISCS = 'brake_discs'
    BRAKE_FLUID = 'brake_fluid'
    BRAKE_LINES = 'brake_lines'
    BRAKE_PADS = 'brake_pads'
    MASTER_CYLINDER = 'master_cylinder'
    TEMPERATURE_CONTROL_AND_MONITORING = 'temperature_control_and_monitoring'
    TIRES = 'tires'
    UNKNOWN = 'unknown'



class TireTypeEnum(Enum):
    SUMMER = 'summer'
    WINTER = 'winter'
    ALL_SEASON = 'all_season'
    ALL_TERRAIN = 'all_terrain'
    ALL_WEATHER = 'all_weather'
    MUD_TERRAIN = 'mud_terrain'
    UNKNOWN = 'unknown'


class AddOnEnum(Enum):
    EXTRA_PURCHASE = 'extra_purchase'
    WARRANTY = 'warranty'
    UNKNOWN = 'unknown'



class TheWheelShopCollectionEnum(Enum):

    # Wheels:
    FOUR_LUGS = '4 Lugs'
    FIVE_LUGS = '5 Lugs'
    SIX_LUGS = '6 Lugs'
    SEVEN_LUGS = '7 Lugs'
    EIGHT_LUGS = '8 Lugs'

    # Tires:
    TIRES_SUMMER = 'Summer Tires'
    TIRES_WINTER = 'Winter Tires'
    TIRES_ALL_TERRAIN = 'All Terrain Tires'
    TIRES_MUD_TERRAIN = 'Mud Terrain Tires'
    
    # Accessories:
    ADAPTER_HUB_RINGS_SPACERS = 'ADAPTERS | HUB RINGS | SPACERS'  # has wheel attributes
    CENTER_CAPS_EMBLEMS_INSERTS = 'CENTER CAPS | EMBLEMS | INSERTS'
    TPMS_VALVES_STUDS = 'TPMS | VALVES | STUDS'
    BOLTS_NUTS = 'BOLTS | NUTS'
    
    # UTV Utility Task Vehicle (similar to an ATV):
    UTV_WHEELS = 'UTV WHEELS'

    # Auto Parts:
    EXHAUST = 'Exhaust'
    INTAKE = 'Intake'
    SUSPENSION = 'Suspension'





class VehicleMakeEnum(Enum):

    ABARATH = "Abarth"
    ACURA = "Acura"
    ALFA_ROMEO = "Alfa Romeo"
    ASTON_MARTON = "Aston Martin"
    AUDI = "Audi"
    BENTLEY = "Bentley"
    BMW = "BMW"
    BUGATTI = "Bugatti"
    CADILLAC = "Cadillac"
    CHEVROLET = "Chevrolet"
    CHRYSLER = "Chrysler"
    CITROEN = "Citroën"
    DACIA = "Dacia"
    DAEWOO = "Daewoo"
    DAIHATSU = "Daihatsu"
    DODGE = "Dodge"
    DONKERVOOT = "Donkervoort"
    DS = "DS"
    FERRARI = "Ferrari"
    FIAT = "Fiat"
    FISKER = "Fisker"
    FORD = "Ford"
    HONDA = "Honda"
    HUMMER = "Hummer"
    HYUNDAI = "Hyundai"
    INFINITI = "Infiniti"
    ISUZU = "Isuzu"
    IVECO = "Iveco"
    JAGUAR = "Jaguar"
    JEEP = "Jeep"
    KIA = "Kia"
    KTM = "KTM"
    LADA = "Lada"
    LAMBORGHINI = "Lamborghini"
    LANCIA = "Lancia"
    LAND_ROVER = "Land Rover"
    LANDWIND = "Landwind"
    LEXUS = "Lexus"
    LOTUS = "Lotus"
    MASTERATI = "Maserati"
    MAYBACH = "Maybach"
    MAZDA = "Mazda"
    MCLAREN = "McLaren"
    MERCEDES_BENZ = "Mercedes-Benz"
    MG = "MG"
    MINI = "Mini"
    MITSUBISHI = "Mitsubishi"
    MORGAN = "Morgan"
    NISSAN = "Nissan"
    OPEL = "Opel"
    PEUGEOT = "Peugeot"
    PORSCHE = "Porsche"
    RENAULT = "Renault"
    ROLLS_ROYCE = "Rolls-Royce"
    SAAB = "Saab"
    SCION = "Scion"
    SKODA = "Skoda"
    SMART = "Smart"
    SSANGYONG = "SsangYong"
    SUBARU = "Subaru"
    SUZUKI = "Suzuki"
    TESLA = "Tesla"
    TOYOTA = "Toyota"
    VOLKSWAGEN = "Volkswagen"
    VOLVO = "Volvo"


class TableLabelEnum(Enum):
    """This is used for transferring DB data to the 
    Speed-Fanatics store DB.
    """
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    SUPPLIER = 'supplier'
    BRAND = 'brand'
    PRODUCT = 'product'
    PRODUCT_VARIATION = 'product_variation'
    VARIATION_TYPE = 'variation_type'
    PRICE = 'price'
    COST = 'cost'
    ADD_ON = 'add_on'
    TIRE_ATTRIBUTE = 'tire_attribute'
    WHEEL_ATTRIBUTE = 'wheel_attribute'
    PRODUCT_IMAGE = 'product_image'
    
 




















