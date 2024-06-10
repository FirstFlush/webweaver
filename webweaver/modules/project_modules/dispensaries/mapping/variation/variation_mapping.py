from enum import Enum


class VariationEnum(Enum):
    GRAM = 1
    TWO_GRAMS = 2
    EIGHTH_OZ = 3.5
    QUARTER_OZ = 7
    HALF_OZ = 14
    OUNCE = 28
    QUARTER_LB = 112
    HALF_LB = 224
    QUARTER_KG = 250
    POUND = 448
    HALF_KG = 500
    KILOGRAM = 1000
    UNKNOWN = None

    # ZERO_POINT_SEVEN_ML = 0.7
    # ONE_ML = 1
    # TWO_ML = 2
    # THREE_ML = 3
    # TWENTY_ML = 20
    # FIFTY_ML = 50
    # HUNDRED_ML = 100



class VariationMap:
    """This class holds mapping for product variations
    in whatever form we encounter them.
    
    variation mappings (g):
        1       gram
        2       2 grams
        3.5     eighth
        7       quarter oz
        14      half oz
        28      oz
        112     quarter lb
        224     half lb
        250     quarter kg
        448     lb
        500     half kg
        1000    kg

    """
    VARIATION_MAP = {
        1: VariationEnum.GRAM,
        1.0: VariationEnum.GRAM,
        '1': VariationEnum.GRAM,
        '1g': VariationEnum.GRAM,
        '1 g': VariationEnum.GRAM,
        'gram': VariationEnum.GRAM,
        '1gram': VariationEnum.GRAM,
        '1-g': VariationEnum.GRAM,
        '1-gram': VariationEnum.GRAM,

        2: VariationEnum.TWO_GRAMS,
        2.0: VariationEnum.TWO_GRAMS,
        '2': VariationEnum.TWO_GRAMS,
        '2g': VariationEnum.TWO_GRAMS,
        '2gram': VariationEnum.TWO_GRAMS,
        '2grams': VariationEnum.TWO_GRAMS,
        '2 g': VariationEnum.TWO_GRAMS,
        '2 gram': VariationEnum.TWO_GRAMS,
        '2 grams': VariationEnum.TWO_GRAMS,
        '2-g': VariationEnum.TWO_GRAMS,
        '2-gram': VariationEnum.TWO_GRAMS,
        '2-grams': VariationEnum.TWO_GRAMS,

        3.5: VariationEnum.EIGHTH_OZ,
        '3.5': VariationEnum.EIGHTH_OZ,
        '3.5g': VariationEnum.EIGHTH_OZ,
        '3.5 g': VariationEnum.EIGHTH_OZ,
        '3.5 gram': VariationEnum.EIGHTH_OZ,
        '3.5 grams': VariationEnum.EIGHTH_OZ,
        '3.5-g': VariationEnum.EIGHTH_OZ,
        '3.5-gram': VariationEnum.EIGHTH_OZ,
        '3.5-grams': VariationEnum.EIGHTH_OZ,
        'eighth': VariationEnum.EIGHTH_OZ,
        'eight ball': VariationEnum.EIGHTH_OZ,
        '1/8': VariationEnum.EIGHTH_OZ,
        '1/8th': VariationEnum.EIGHTH_OZ,
        '1/8oz': VariationEnum.EIGHTH_OZ,
        '1/8 oz': VariationEnum.EIGHTH_OZ,
        '1/8 ounce': VariationEnum.EIGHTH_OZ,
        '3-5-g': VariationEnum.EIGHTH_OZ,
        '3-5-gram': VariationEnum.EIGHTH_OZ,
        '3-5-grams': VariationEnum.EIGHTH_OZ,
        '1-8-oz': VariationEnum.EIGHTH_OZ,
        '1-8-ounce': VariationEnum.EIGHTH_OZ,
        'eighth-oz': VariationEnum.EIGHTH_OZ,
        'eighth-ounce': VariationEnum.EIGHTH_OZ,

        7: VariationEnum.QUARTER_OZ,
        7.0: VariationEnum.QUARTER_OZ,
        '7': VariationEnum.QUARTER_OZ,
        '7g': VariationEnum.QUARTER_OZ,
        '7gram': VariationEnum.QUARTER_OZ,
        '7grams': VariationEnum.QUARTER_OZ,
        '1/4': VariationEnum.QUARTER_OZ,
        '1/4th': VariationEnum.QUARTER_OZ,
        '1/4oz': VariationEnum.QUARTER_OZ,
        '1/4 oz': VariationEnum.QUARTER_OZ,
        '1/4 ounce': VariationEnum.QUARTER_OZ,
        '7 g': VariationEnum.QUARTER_OZ,
        '7 gram': VariationEnum.QUARTER_OZ,
        '7 grams': VariationEnum.QUARTER_OZ,
        '7-g': VariationEnum.QUARTER_OZ,
        '7-gram': VariationEnum.QUARTER_OZ,
        '7-grams': VariationEnum.QUARTER_OZ,
        'quarter oz': VariationEnum.QUARTER_OZ,
        'quarter ounce': VariationEnum.QUARTER_OZ,
        'quarter zip': VariationEnum.QUARTER_OZ,
        '1-4-oz': VariationEnum.QUARTER_OZ,
        '1-4-ounce': VariationEnum.QUARTER_OZ,
        'quarter-oz': VariationEnum.QUARTER_OZ,
        'quarter-ounce': VariationEnum.QUARTER_OZ,

        14: VariationEnum.HALF_OZ,
        14.0: VariationEnum.HALF_OZ,
        '14': VariationEnum.HALF_OZ,
        '14g': VariationEnum.HALF_OZ,
        '14gram': VariationEnum.HALF_OZ,
        '14grams': VariationEnum.HALF_OZ,
        '14 g': VariationEnum.HALF_OZ,
        '14 gram': VariationEnum.HALF_OZ,
        '14 grams': VariationEnum.HALF_OZ,
        '14-g': VariationEnum.HALF_OZ,
        '14-gram': VariationEnum.HALF_OZ,
        '14-grams': VariationEnum.HALF_OZ,
        '1/2': VariationEnum.HALF_OZ,
        '1/2oz': VariationEnum.HALF_OZ,
        '1/2 oz': VariationEnum.HALF_OZ,
        '1/2 ounce': VariationEnum.HALF_OZ,
        'half oz': VariationEnum.HALF_OZ,
        'half ounce': VariationEnum.HALF_OZ,
        'half zip': VariationEnum.HALF_OZ,
        '1-2-oz': VariationEnum.HALF_OZ,
        '1-2-ounce': VariationEnum.HALF_OZ,
        'half-oz': VariationEnum.HALF_OZ,
        'half-ounce': VariationEnum.HALF_OZ,

        28: VariationEnum.OUNCE,
        28.0: VariationEnum.OUNCE,
        '28': VariationEnum.OUNCE,
        '28g': VariationEnum.OUNCE,
        '28gram': VariationEnum.OUNCE,
        '28grams': VariationEnum.OUNCE,
        '28 g': VariationEnum.OUNCE,
        '28 gs': VariationEnum.OUNCE,
        '28 gram': VariationEnum.OUNCE,
        '28 grams': VariationEnum.OUNCE,
        '28-g': VariationEnum.OUNCE,
        '28-gs': VariationEnum.OUNCE,
        '28-gram': VariationEnum.OUNCE,
        '28-grams': VariationEnum.OUNCE,
        '28grams': VariationEnum.OUNCE,
        'oz':VariationEnum.OUNCE,
        'ounce': VariationEnum.OUNCE,
        'zip': VariationEnum.OUNCE,
        '1oz': VariationEnum.OUNCE,
        '1-oz': VariationEnum.OUNCE,
        '1-ounce': VariationEnum.OUNCE,
        '1 oz': VariationEnum.OUNCE,
        '1 ounce': VariationEnum.OUNCE,

        112: VariationEnum.QUARTER_LB,
        112.0: VariationEnum.QUARTER_LB,
        '112': VariationEnum.QUARTER_LB,
        '112g': VariationEnum.QUARTER_LB,
        '1/4lb': VariationEnum.QUARTER_LB,
        '1/4pound': VariationEnum.QUARTER_LB,
        '1/4 lb': VariationEnum.QUARTER_LB,
        '1/4 pound': VariationEnum.QUARTER_LB,
        'quarter lb': VariationEnum.QUARTER_LB,
        'quarter pound': VariationEnum.QUARTER_LB,
        '1-4-lb': VariationEnum.QUARTER_LB,
        '1-4-pound': VariationEnum.QUARTER_LB,

        224: VariationEnum.HALF_LB,
        224.0: VariationEnum.HALF_LB,
        '224': VariationEnum.HALF_LB,
        '224g': VariationEnum.HALF_LB,
        '1/2lb': VariationEnum.HALF_LB,
        '1/2 lb': VariationEnum.HALF_LB,
        '1/2pound': VariationEnum.HALF_LB,
        '1/2 pound': VariationEnum.HALF_LB,
        'half lb': VariationEnum.HALF_LB,
        'half pound': VariationEnum.HALF_LB,
        '1-2-lb': VariationEnum.HALF_LB,
        'half-lb' : VariationEnum.HALF_LB,

        250: VariationEnum.HALF_KG,
        250.0: VariationEnum.HALF_KG,
        '250': VariationEnum.HALF_KG,
        '250g': VariationEnum.HALF_KG,
        '1/4kg': VariationEnum.HALF_KG,
        '1/4 kg': VariationEnum.HALF_KG,
        '1/4 kilo': VariationEnum.HALF_KG,
        '1/4 kilogram': VariationEnum.HALF_KG,
        'quarter kg': VariationEnum.HALF_KG,
        'quarter kilo': VariationEnum.HALF_KG,
        'quarter kilogram': VariationEnum.HALF_KG,
        '1-4-kg': VariationEnum.HALF_KG,
        '1-4-kilo': VariationEnum.HALF_KG,
        '1-4-kilogram': VariationEnum.HALF_KG,

        448: VariationEnum.POUND,
        448.0: VariationEnum.POUND,
        '448': VariationEnum.POUND,
        '448g': VariationEnum.POUND,
        '1lb': VariationEnum.POUND,
        '1 lb': VariationEnum.POUND,
        '1 pound': VariationEnum.POUND,
        'lb': VariationEnum.POUND,
        'pound': VariationEnum.POUND,
        '1-lb': VariationEnum.POUND,
        '1-pound': VariationEnum.POUND,

        500: VariationEnum.HALF_KG,
        500.0: VariationEnum.HALF_KG,
        '500': VariationEnum.HALF_KG,
        '500g': VariationEnum.HALF_KG,
        '1/2kg': VariationEnum.HALF_KG,
        '1/2 kg': VariationEnum.HALF_KG,
        '1/2 kilo': VariationEnum.HALF_KG,
        '1/2 kilogram': VariationEnum.HALF_KG,
        'half kg': VariationEnum.HALF_KG,
        'half kilo': VariationEnum.HALF_KG,
        'half kilogram': VariationEnum.HALF_KG,
        '1-2-kg': VariationEnum.HALF_KG,
        '1-2-kilo': VariationEnum.HALF_KG,
        '1-2-kilogram': VariationEnum.HALF_KG,

        1000: VariationEnum.KILOGRAM,
        1000.0: VariationEnum.KILOGRAM,
        '1000': VariationEnum.KILOGRAM,
        '1000g': VariationEnum.KILOGRAM,
        'kg': VariationEnum.KILOGRAM,
        'kilo': VariationEnum.KILOGRAM,
        'kilogram': VariationEnum.KILOGRAM,
        '1-kg': VariationEnum.KILOGRAM,
        '1-kilo': VariationEnum.KILOGRAM,
    }
