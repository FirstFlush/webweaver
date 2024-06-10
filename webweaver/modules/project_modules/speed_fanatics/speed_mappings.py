from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    TheWheelShopCollectionEnum, 
    CategoryEnum, 
    SubCategoryEnum,
    WheelAttributeEnum,
    TireAttributeEnum,
    DataTypeEnum
)


class SpeedMapping:
    """This class holds the various dictionary mappings used by spiders to match
    scraped text to its associated enum or model.
    """

    text_to_data_type = {
        'finish': DataTypeEnum.STRING,
        'package': DataTypeEnum.STRING,
    }

    data_type_to_type = {
        DataTypeEnum.STRING : str,
        DataTypeEnum.FLOAT: float,
        DataTypeEnum.INTEGER: int,
        DataTypeEnum.UNKNOWN: str,
    }



    text_to_wheel_attribute = {
        'size': WheelAttributeEnum.WHEEL_SIZE,
    }

    text_to_tire_attribute = {
        'loadrating': TireAttributeEnum.LOAD_INDEX,
        'profile': TireAttributeEnum.ASPECT_RATIO,
        'speedrating': TireAttributeEnum.SPEED_RATING,
        'od': TireAttributeEnum.OVERALL_DIAMETER,
        'width': TireAttributeEnum.TIRE_WIDTH
        # 'studs': TireAttributeEnum.STUDDABLE,
    }

    text_to_subcategory_enum = {
        'winter': SubCategoryEnum.TIRES_WINTER,
        'summer': SubCategoryEnum.TIRES_SUMMER,
        'allseason': SubCategoryEnum.TIRES_ALL_SEASON,
        'allweather': SubCategoryEnum.TIRES_ALL_WEATHER,
        'tiresoftener': SubCategoryEnum.TIRES_MISC
    }


    subcategory_enum_to_category_enum = {
        # Brakes
        SubCategoryEnum.BRAKE_BUNDLES : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_CALIPERS : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_DISCS : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_FLUIDS : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_KITS : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_LINES : CategoryEnum.BRAKES,
        SubCategoryEnum.BRAKE_PADS : CategoryEnum.BRAKES,
        # Exhaust
        SubCategoryEnum.EXHAUST_SYSTEMS : CategoryEnum.EXHAUST,
        # Intake
        SubCategoryEnum.AIR_FILTERS : CategoryEnum.INTAKE,
        # Racewear
        SubCategoryEnum.BOOTS : CategoryEnum.RACEWEAR,
        SubCategoryEnum.CLOTHING : CategoryEnum.RACEWEAR,
        SubCategoryEnum.GLOVES : CategoryEnum.RACEWEAR,
        SubCategoryEnum.HELMETS : CategoryEnum.RACEWEAR,
        SubCategoryEnum.SUITS : CategoryEnum.RACEWEAR,
        # Suspension
        SubCategoryEnum.BAR_BUSHINGS : CategoryEnum.SUSPENSION,
        SubCategoryEnum.SHOCK_ABSORBERS : CategoryEnum.SUSPENSION,
        SubCategoryEnum.SPRINGS : CategoryEnum.SUSPENSION,
        SubCategoryEnum.STRUTS : CategoryEnum.SUSPENSION,
        SubCategoryEnum.SWAY_BARS : CategoryEnum.SUSPENSION,
        # Tires
        SubCategoryEnum.TIRES_ALL_SEASON : CategoryEnum.TIRES,
        SubCategoryEnum.TIRES_ALL_WEATHER : CategoryEnum.TIRES,
        SubCategoryEnum.TIRES_ALL_TERRAIN : CategoryEnum.TIRES,
        SubCategoryEnum.TIRES_MUD : CategoryEnum.TIRES,
        SubCategoryEnum.TIRES_SUMMER : CategoryEnum.TIRES,
        SubCategoryEnum.TIRES_WINTER : CategoryEnum.TIRES,
        # Tire Accessories
        SubCategoryEnum.TIRES_MISC : CategoryEnum.TIRE_ACCESSORIES,
        SubCategoryEnum.TIRES_STUDS : CategoryEnum.TIRE_ACCESSORIES,
        SubCategoryEnum.TIRES_VALVES : CategoryEnum.TIRE_ACCESSORIES,
        SubCategoryEnum.TPMS : CategoryEnum.TIRE_ACCESSORIES,
        # Wheels
        SubCategoryEnum.WHEELS_AUTOMOTIVE : CategoryEnum.WHEELS,
        SubCategoryEnum.WHEELS_UTV_ATV : CategoryEnum.WHEELS,
        #WheelAccessories
        SubCategoryEnum.WHEEL_ADAPTERS : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_CAPS : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_HUB_RINGS : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_MISC : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_NUTS_BOLTS : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_RIVETS : CategoryEnum.WHEEL_ACCESSORIES,
        SubCategoryEnum.WHEEL_SPACERS : CategoryEnum.WHEEL_ACCESSORIES,
    }




    collection_enum_to_category_enum = {
        # Wheels
        TheWheelShopCollectionEnum.FOUR_LUGS : CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.FIVE_LUGS :CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.SIX_LUGS : CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.SEVEN_LUGS : CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.EIGHT_LUGS : CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.UTV_WHEELS : CategoryEnum.WHEELS,
        TheWheelShopCollectionEnum.ADAPTER_HUB_RINGS_SPACERS : CategoryEnum.WHEELS,

        # Tires
        TheWheelShopCollectionEnum.TIRES_ALL_TERRAIN : CategoryEnum.TIRES,
        TheWheelShopCollectionEnum.TIRES_MUD_TERRAIN : CategoryEnum.TIRES,
        TheWheelShopCollectionEnum.TIRES_SUMMER : CategoryEnum.TIRES,
        TheWheelShopCollectionEnum.TIRES_WINTER : CategoryEnum.TIRES,
    }


