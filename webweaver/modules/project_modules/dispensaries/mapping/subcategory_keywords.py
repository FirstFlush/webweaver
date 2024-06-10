from enum import Enum
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import SubCategoryEnum, CategoryEnum


class HelperKeywords:

    FRUIT = 'fruit'


class SubCategoryKeyWords:
    """Sets of keywords to be used to determine product subcategory.
    These sets are either: 
        1) intersected with a set made of the scraped product title/name's words
        2) each string in set can be used as substring search of product title/name
    """


        


    keyword_sets = {
    # Accessories
    # =========================================
        CategoryEnum.ACCESSORIES : {

            SubCategoryEnum.BATTERIES : {
                'battery',
                'batteries',
            },

            SubCategoryEnum.CLOTHING : {
                'clothing',
                'clothes',
                'collar',
                'shirt',
                'shirts',
                'pants',
                'hat',
                'hats',
                'apparel',
                'hooded'
                'hoodie',
                'hoodies',
                'threads',  #stupid
                'shirt',
                'shirts',
                'tshirt',
                'tshirts',
                't-shirt',
                't-shirts',
                'belt',
                'belts',
                'toque',
                'toques',
                'tuque',
                'tuques',
                'touque',
                'touques',
                'beanie',
                'beanies',
            },

            SubCategoryEnum.GRINDERS : {
                'grinder',
                'grinders',
                'buster',
                'busters'
            },

            SubCategoryEnum.LIGHTERS : {
                'lighter',
                'lighters',
            },

            SubCategoryEnum.MISC : {
                'misc',
                'misc.',
                'miscellaneous',
                'miscelleneous',
                'ash',
                'tray',
                'ashtray',
                'ash-tray',
                'wallet',
                'book',
                'booklet',
                'silicon',
                'silicone',
                'mat',
                'mats',
                'wrap',
                'wraps',
            },

            SubCategoryEnum.PIPES : {
                'pipe',
                'pipes',
                'glassware',
                'crystal',
                'glass',
            },

            SubCategoryEnum.ROLLING_PAPERS : {
                'rolling',
                'paper',
                'papers',
                'rollies',
                'filter',
                'filters',
                'filtered',
            },
        },
        # Bulk
        # =========================================
        CategoryEnum.BULK : {
            SubCategoryEnum.BULK_CONCENTRATES : {
                'budder',
                'concentrate',
                'concentrates',
                'd9',
                'd-9',
                'd8',
                'd-8',
                'dist',
                'budder',
                'butane',
                'bho',
                'distillate',
                'dist',
                'sauce',
                'wax',
                'resin',
                'rosin',
                'liveresin',
                'solventless',
                'solvent',
                'shatter',
            },

            SubCategoryEnum.BULK_EDIBLES : {
                'edible',
                'edibles',
                'gummies',
                'chocolates',
                'candies',
                'candy',
                'kandy',
                'kandies',
                'chips',
                'gummy',
                'jelly',
            },

            SubCategoryEnum.BULK_FLOWER : {
                'weed',
                'flower',
                'flowers',
                'ganja',
                'bud',
                'buds',
                'herb',
                'herbs',
            },

            SubCategoryEnum.BULK_HASH : {
                'hash',
                'hashish',
            },
        },

        # CBD
        # =========================================
        CategoryEnum.CBD : {
                
            SubCategoryEnum.CBD_CAPSULES : {
                'caps',
                'capsules',
                'gel',
            },

            SubCategoryEnum.CBD_EDIBLES : {
                'astronaut',
                'astronauts',
                'baked',
                'baked-goods',
                'beverage',
                'beverages',
                'edible',
                'edibles',
                'gummy',
                'gummies',
                'chocolate',
                'chocolates',
                'candies',
                'candy',
                'chips',
                'jelly',
                'jellies',
                'honey',
            },

            SubCategoryEnum.CBD_ISOLATE : {
                'isolate',
                'bulk',
                'powder',
            },

            SubCategoryEnum.CBD_OIL : {
                'oil',
            },

            SubCategoryEnum.CBD_PETS : {
                'pet',
                'pets',
                'dog',
                'dogs',
                'cat',
                'cats',
                'animal',
                'furry',
                'four-legged',
            },

            SubCategoryEnum.CBD_TINCTURES : {
                'tincture',
                'tinctures',
                'sublingual',
                'sublingually',
            },

            SubCategoryEnum.CBD_TOPICALS : {
                'topical',
                'topicals',
                'ointment',
                'ointments',
                'rub',
                'rubs',
                'rubbing',
                'spray',
                'sprays',
                'stick',
                'sticks',
                'roll',
                'rolls',
                'roller',
                'skin',
                'eye',
                'eyes',
                'hair',
            },

            SubCategoryEnum.CBD_VAPES : {
                'vape',
                'vapes',
                'cart',
                'carts',
                'cartridge',
                'cartridges',
                'atomizer',
                'vaporizor',
                'vaporizors',
                'vaporizer',
                'vaporizers',
            },
        },
        # Concentrates
        # =========================================
        CategoryEnum.CONCENTRATES : {
                
            SubCategoryEnum.BUDDER : {
                'budder',
            },

            SubCategoryEnum.DIAMONDS : {
                'diamond',
                'diamonds',
            },

            SubCategoryEnum.DISTILLATE : {
                'distillate',
                'dist',
                'd8',
                'd9',
                'd-8',
                'd-9',
            },

            SubCategoryEnum.HASH : {
                'hash',
                'hashish',
            },

            SubCategoryEnum.HTFSE : {
                'htfse',
                'full-spectrum',
            },

            SubCategoryEnum.KIEF : {
                'kief',
            },

            SubCategoryEnum.LIVE_RESIN : {
                'live-resin',
                'resin',
                'liveresin',
            },

            SubCategoryEnum.PHOENIX_TEARS : {
                'phoenix',
                'phoenix-tear',
                'phoenix-tears',
                'tears',
                'tear',
            },

            SubCategoryEnum.ROSIN : {
                'rosin',
                'live-rosin',
                'liverosin',
            },

            SubCategoryEnum.SAUCE : {
                'sauce',
            },

            SubCategoryEnum.SHATTER : {
                'shatter',
            },

            SubCategoryEnum.WAX : {
                'wax',
            },
        },

        # Edibles
        # =========================================

        CategoryEnum.EDIBLES : {
                
            SubCategoryEnum.BAKED_GOODS : {
                'cookie',
                'cookies',
                'brownie',
                'brownies',
                'baked',
                'pastry',
                'pastries',
            },

            SubCategoryEnum.BEVERAGES : {
                'beverage',
                'beverages',
                'drink',
                'drinks',
                'coffee',
                'tea',
                'icedtea',
                'iced-tea',
            },

            SubCategoryEnum.CANDY : {
                'astronaut',
                'astronauts',
                'blast',
                'blasts',
                'candy',
                'candies',
                'kandy',
                'kandies',
                'cream',
                'custard',
                'gelato',
                'gummy',
                'gummies',
                'sweets',
                'jelly',
                'jellies',
                'drops',
                'bomb',
                'bombs',
                'blocks',
                'bricks',
                'sours',
                'cola',
                'colas',
                'soda',
                'sodas',
                'bears',
                'chewies',
                'chews',
                'colas',
                'worms',
                'dolphins',
                'marshmallow',
                'marshmallows',
                'sherbet',
                'sherbert',
                'sorbet',
                'sorbetto',
                'caramels',
                'caramel',
                'cara-melts',
                'pops,'
                'frosting',
                'honey',
            },

            SubCategoryEnum.CAPSULES : {
                'caps',
                'capsules',
                'gel-cap',
                'gel',
            },

            SubCategoryEnum.CHOCOLATE : {
                'chocolate',
                'cocoa',
                'cacao',
                'chocolatey',
                'chocolates',
                'choklit',
                'chocolit',
                'chok-lit',
            },

            SubCategoryEnum.OIL : {
                'oil',
                'oils',
                'simpson',
                'rick-simpson',
                'rick-simpson-oil',
                'rso',
                'v-rso',
                'vrso',
            },

            SubCategoryEnum.TINCTURES : {
                'tincture',
                'tinctures',
                'spray',
                'sublingual',
                'sublingually',
            },
        },

        # Flower
        # =========================================

        CategoryEnum.FLOWER : {
            
            SubCategoryEnum.INDICA : {
                'indica',
            },

            SubCategoryEnum.INFUSED : {
                'infused',
                'infusion',
            },

            SubCategoryEnum.HYBRID : {
                'hybrid',
            },

            SubCategoryEnum.PREROLL : {
                'preroll',
                'prerolls',
                'prerolled',
                'pre-roll',
                'pre-rolls',
                'pre-rolled',
            },

            SubCategoryEnum.SATIVA : {
                'sativa',
            },

            SubCategoryEnum.SHAKE : {
                'shake',
            }
        },

        # Vapes
        # =========================================

        CategoryEnum.VAPES : {
            SubCategoryEnum.BATTERIES : {
                'battery',
                'batteries',
            },

            SubCategoryEnum.CARTS : {
                'vape',
                'juice',
                'pen',
                'pens',
                'cart',
                'carts',
                'cartridge',
                'cartridges',
                'vaporizor',
                'vaporizors',
                'vaporizer',
                'vaporizers',
                'dist',
                'distillate',
                'd8',
                'd9',
                'live-resin',
                'live-rosin',
                'resin',
                'rosin',
                'htfse',
                'terpene',
                'extract',
                'oil',
                'sauce',
                'pressed',
            },

            SubCategoryEnum.DISPOSABLE : {
                'disposable',
                'throw-away',
                'throw-aways',
            },
        },


        # Additional helper sets
        # =========================================
        HelperKeywords.FRUIT : {
            'apple',
            'apricot',
            'avocado',
            'banana',
            'berries',
            'berry',
            'carribbean',
            'cantaloupe',
            'cherimoya',
            'cherry',
            'cherries',
            'chico',
            'citrus',
            'clementine',
            'coconut',
            'cucumber',
            'currant',
            'damson',
            'date',
            'durian',
            'feijoa',
            'fig',
            'fruit',
            'goji',
            'grape',
            'guava',
            'honeydew',
            'jabuticaba',
            'jambul',
            'jujube',
            'juniper',
            'kiwano',
            'kiwi',
            'kumquat',
            'lemon',
            'lime',
            'longan',
            'loquat',
            'lychee',
            'mandarine',
            'mango',
            'melon',
            'nance',
            'naranjilla',
            'nectarine',
            'orange',
            'papaya',
            'peach',
            'pear',
            'persimmon',
            'physalis',
            'plantain',
            'plum',
            'pomegranate',
            'pomelo',
            'prune',
            'punch',
            'quince',
            'raisin',
            'rambutan',
            'redcurrant',
            'salak',
            'salal',
            'satsuma',
            'solanum',
            'soursop',
            'sultana',
            'tamarillo',
            'tamarind',
            'tangerine',
            'tropical',
            'yuzu',
        },

    }





















# CATEGORIES & SUB-CATEGORIES
#     accessories
#         clothing
#         grinders
#         lighters
#         misc
#         pipes
#         rollies
#     bulk
#         bulk concentrates
#         bulk edibles
#         bulk flower
#         bulk hash
#     cbd
#         cbd capsules
#         cbd edibles
#         cbd isolate
#         cbd tinctures
#         cbd oil (also tears?)
#         cbd pets
#         cbd vapes
#     concentrates
#         budder
#         diamonds
#         distillate
#         htfse
#         hash
#         kief
#         live resin
#         phoenix tears
#         rosin
#         sauce
#         shatter
#         wax
#     flower
#         hybrid
#         indica
#         infused (ie moon rocks)
#         preroll
#         sativa
#     vapes
#         batteries
#         carts
#         disposable
#     edibles
#         candy/gummies
#         capusules
#         chocolate
#         drinks
#         baked goods
#         oils/tinctures
#     unknown
#         unknown
