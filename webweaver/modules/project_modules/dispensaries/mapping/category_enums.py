from enum import Enum



class CategoryEnum(Enum):

    ACCESSORIES = 'accessories'
    BULK = 'bulk'
    BUNDLE = 'bundle'
    CBD = 'cbd'
    CONCENTRATES = 'concentrates'
    EDIBLES = 'edibles'
    FLOWER = 'flower'
    VAPES = 'vapes'
    UNKNOWN = 'unknown'

class SubCategoryEnum(Enum):
    # Accessories
    CLOTHING = 'clothing'
    GRINDERS = 'grinders'
    LIGHTERS = 'lighters'
    PIPES = 'pipes'
    ROLLING_PAPERS = 'rolling_papers'
    MISC = 'misc'
    # Bulk
    BULK_CONCENTRATES = 'bulk_concenrates'
    BULK_EDIBLES = 'bulk_edibles'
    BULK_FLOWER = 'bulk_flower'
    BULK_HASH = 'bulk_hash'
    # Bundle
    BUNDLE_CBD = 'bundle_cbd'
    BUNDLE_CONCENTRATES = 'bundle_concentrates'
    BUNDLE_CROSS_CATEGORY = 'bundle_cross_category'
    BUNDLE_EDIBLES = 'bundle_edibles'
    BUNDLE_FLOWER = 'bundle_flower'
    BUNDLE_MISC = 'bundle_misc'
    BUNDLE_UNKNOWN = 'bundle_unknown'
    BUNDLE_VAPES = 'bundle_vapes'
    # CBD
    CBD_CAPSULES = 'cbd_capsules'
    CBD_EDIBLES = 'cbd_edibles'
    CBD_ISOLATE = 'cbd_isolate'
    CBD_OIL = 'cbd_oil'
    CBD_PETS = 'cbd_pet'
    CBD_TINCTURES = 'cbd_tinctures'
    CBD_TOPICALS = 'cbd_topicals'
    CBD_VAPES = 'cbd_vapes'
    # Concentrates
    BUBBLE_HASH = 'bubble_hash'
    BUDDER = 'budder'
    DIAMONDS = 'diamonds'
    DISTILLATE = 'distillate'
    HTFSE = 'htfse'
    HASH = 'hash'
    KIEF = 'kief'
    LIVE_RESIN = 'live_resin'
    PHOENIX_TEARS = 'phoenix_tears'
    ROSIN = 'rosin'
    SAUCE = 'sauce'
    SHATTER = 'shatter'
    WAX = 'wax'
    # Edibles
    BAKED_GOODS = 'baked_goods'
    BEVERAGES = 'beverages'
    CANDY = 'candy'
    CAPSULES = 'capsules'
    CHOCOLATE = 'chocolate'
    OIL = 'oil'
    TINCTURES = 'tinctures'
    # Flower
    HYBRID = 'hybrid'
    INDICA = 'indica'
    INFUSED = 'infused'
    PREROLL = 'preroll'
    SATIVA = 'sativa'
    SHAKE = 'shake'
    # Vapes
    BATTERIES = 'batteries'
    CARTS = 'carts'
    DISPOSABLE = 'disposable'

    UNKNOWN = 'unknown'


class CategoryEnumMap:
    """This is useful because it allows us to instantly determine an UNKNOWN category
    if we have successfully determined the subcategory . 
    By keeping this mapping in
    code rather than in the DB (as a foreignkey from SubCategory => Category) it
    allows greater flexibility and extensibility in structuring our categorization
    system.

    ^ Wtf kind of legalese bullshit is this?
    """
    subcategory_enum_to_category_enum = {
        # Accessories
        SubCategoryEnum.CLOTHING : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.GRINDERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.LIGHTERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.PIPES : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.ROLLING_PAPERS : CategoryEnum.ACCESSORIES,
        SubCategoryEnum.MISC : CategoryEnum.ACCESSORIES,
        # Bulk
        SubCategoryEnum.BULK_CONCENTRATES : CategoryEnum.BULK,
        SubCategoryEnum.BULK_EDIBLES : CategoryEnum.BULK,
        SubCategoryEnum.BULK_FLOWER : CategoryEnum.BULK,
        SubCategoryEnum.BULK_HASH : CategoryEnum.BULK,
        # Bundle
        SubCategoryEnum.BUNDLE_CBD : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_CONCENTRATES : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_CROSS_CATEGORY : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_EDIBLES : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_FLOWER : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_MISC : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_UNKNOWN : CategoryEnum.BUNDLE,
        SubCategoryEnum.BUNDLE_VAPES : CategoryEnum.BUNDLE,
        # CBD
        SubCategoryEnum.CBD_CAPSULES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_EDIBLES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_ISOLATE : CategoryEnum.CBD,
        SubCategoryEnum.CBD_OIL : CategoryEnum.CBD,
        SubCategoryEnum.CBD_PETS : CategoryEnum.CBD,
        SubCategoryEnum.CBD_TINCTURES : CategoryEnum.CBD,
        SubCategoryEnum.CBD_TOPICALS : CategoryEnum.CBD,
        SubCategoryEnum.CBD_VAPES : CategoryEnum.CBD,
        # Concentrates
        SubCategoryEnum.BUBBLE_HASH : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.BUDDER : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.DIAMONDS : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.DISTILLATE : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.HTFSE : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.HASH : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.KIEF : CategoryEnum.CONCENTRATES,
        SubCategoryEnum.LIVE_RESIN: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.PHOENIX_TEARS: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.ROSIN: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.SAUCE: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.SHATTER: CategoryEnum.CONCENTRATES,
        SubCategoryEnum.WAX: CategoryEnum.CONCENTRATES,
        # Edibles
        SubCategoryEnum.BAKED_GOODS : CategoryEnum.EDIBLES,
        SubCategoryEnum.BEVERAGES : CategoryEnum.EDIBLES,
        SubCategoryEnum.CANDY : CategoryEnum.EDIBLES,
        SubCategoryEnum.CAPSULES : CategoryEnum.EDIBLES,
        SubCategoryEnum.CHOCOLATE : CategoryEnum.EDIBLES,
        SubCategoryEnum.OIL : CategoryEnum.EDIBLES,
        SubCategoryEnum.TINCTURES : CategoryEnum.EDIBLES,
        # Flower
        SubCategoryEnum.HYBRID : CategoryEnum.FLOWER,
        SubCategoryEnum.INDICA : CategoryEnum.FLOWER,
        SubCategoryEnum.INFUSED : CategoryEnum.FLOWER,
        SubCategoryEnum.PREROLL : CategoryEnum.FLOWER,
        SubCategoryEnum.SATIVA : CategoryEnum.FLOWER,
        SubCategoryEnum.SHAKE : CategoryEnum.FLOWER,
        # Vapes
        SubCategoryEnum.BATTERIES : CategoryEnum.VAPES,
        SubCategoryEnum.CARTS : CategoryEnum.VAPES,
        SubCategoryEnum.DISPOSABLE : CategoryEnum.VAPES,
    }


    # mapping = {
    #     # Accessories
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.CLOTHING,
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.GRINDERS,
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.LIGHTERS,
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.PIPES,
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.ROLLING_PAPERS,
    #     CategoryEnum.ACCESSORIES : SubCategoryEnum.MISC,
    #     # Bulk
    #     CategoryEnum.BULK : SubCategoryEnum.BULK_CONCENTRATES,
    #     CategoryEnum.BULK : SubCategoryEnum.BULK_EDIBLES,
    #     CategoryEnum.BULK : SubCategoryEnum.BULK_FLOWER,
    #     CategoryEnum.BULK : SubCategoryEnum.BULK_HASH,
    #     # CBD
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_CAPSULES,
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_EDIBLES,
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_ISOLATE,
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_OIL,
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_PET,
    #     CategoryEnum.CBD : SubCategoryEnum.CBD_VAPES,
    #     # Concentrates
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.BUBBLE_HASH,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.BUDDER,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.DIAMONDS,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.DISTILLATE,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.HTFSE,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.HASH,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.KIEF,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.LIVE_RESIN,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.PHOENIX_TEARS,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.ROSIN,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.SHATTER,
    #     CategoryEnum.CONCENTRATES : SubCategoryEnum.WAX,
    #     # Edibles
    #     CategoryEnum.EDIBLES : SubCategoryEnum.BAKED_GOODS,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.BEVERAGES,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.CANDY,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.CAPSULES,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.CHOCOLATE,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.OIL,
    #     CategoryEnum.EDIBLES : SubCategoryEnum.TINCTURES,
    #     # Flower
    #     CategoryEnum.FLOWER : SubCategoryEnum.HYBRID,
    #     CategoryEnum.FLOWER : SubCategoryEnum.INDICA,
    #     CategoryEnum.FLOWER : SubCategoryEnum.INFUSED,
    #     CategoryEnum.FLOWER : SubCategoryEnum.PREROLL,
    #     CategoryEnum.FLOWER : SubCategoryEnum.SATIVA,
    #     # Vapes
    #     CategoryEnum.VAPES : SubCategoryEnum.BATTERIES,
    #     CategoryEnum.VAPES : SubCategoryEnum.CARTS,
    #     CategoryEnum.VAPES : SubCategoryEnum.DISPOSABLE,
    # }