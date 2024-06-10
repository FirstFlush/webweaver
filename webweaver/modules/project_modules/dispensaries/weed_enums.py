from enum import Enum


class CannabisTypeEnum(Enum):
    HYBRID  = 'hybrid'
    INDICA  = 'indica'
    SATIVA  = 'sativa'
    UNKNOWN = 'unknown'



class BudRatingEnum(Enum):
    AAAAA = "AAAAA"
    AAAA = "AAAA"
    AAA = "AAA"
    AA = "AA"
    A_PLUS = "A+"
    A = "A"


class VariationTypeEnum(Enum):
    GRAMS = 'grams'
    ML = 'ml'
    COLOR = 'color'
    SIZE_STR = 'size_str'
    SIZE_NUM = 'size_num'
    UNKNOWN = 'unknown'


