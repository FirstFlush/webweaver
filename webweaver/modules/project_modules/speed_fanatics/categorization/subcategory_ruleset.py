import re
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum,
    SubCategoryEnum,
    MatchMode,
)


class SubCategoryRuleset:

    category_enum_to_subcategory_rules = {
        CategoryEnum.AUTOBODY: {

            SubCategoryEnum.AUTOBODY_MISC: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                },
            },
            SubCategoryEnum.BODY_KITS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                },
            },
            SubCategoryEnum.DIFFUSERS: {
                MatchMode.KEYWORDS: {
                    'diffuser',
                    'diffusers',
                },
                MatchMode.SUBSTRINGS: {

                },
            },
            SubCategoryEnum.SPOILERS: {
                MatchMode.KEYWORDS: {
                    'spoiler',
                    'spoilers',
                },
                MatchMode.SUBSTRINGS: {

                },
            },
        },

        CategoryEnum.BRAKES: {

            SubCategoryEnum.BRAKE_BUNDLES: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'brakebundle',
                },
                MatchMode.REGEX: [
                    re.compile(r'brake.*?bundle(?:s)?'),
                ]

            },

            SubCategoryEnum.BRAKE_CALIPERS: {
                MatchMode.KEYWORDS: {
                    'calipers',
                    'caliper',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.BRAKE_DISCS: {
                MatchMode.KEYWORDS: {
                    'disc',
                    'discs',
                },
                MatchMode.SUBSTRINGS: {
                    'jhook',
                },
                MatchMode.REGEX : [
                    re.compile(r'brake.*?disc(?:s)?'),
                ]

            },

            SubCategoryEnum.BRAKE_FLUIDS: {
                MatchMode.KEYWORDS: {
                },

                MatchMode.SUBSTRINGS: {
                    'brakefluid',
                    'brakehydraulic',
                },
            },

            SubCategoryEnum.BRAKE_KITS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'brakekit',
                },
                MatchMode.REGEX : [
                    re.compile(r'brake.*?kit(?:s)?'),
                ]
            },

            SubCategoryEnum.BRAKE_LINES: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'brakeline',
                },
            },

            SubCategoryEnum.BRAKE_PADS: {
                MatchMode.KEYWORDS: {
                    'pads',
                },
                MatchMode.SUBSTRINGS: {
                    'brakepad',
                },
            },
            
            SubCategoryEnum.MASTER_CYLINDERS: {
                MatchMode.KEYWORDS: {
                    'cylinder',
                    'master',
                },
                MatchMode.SUBSTRINGS: {
                    'mastercylinder',
                },
            },
        },

        CategoryEnum.EXHAUST: {

            SubCategoryEnum.EXHAUST_SYSTEMS: {
                MatchMode.KEYWORDS: {
                    'exhaust',
                },
                MatchMode.SUBSTRINGS: {
                    'catback',
                    'axleback',
                },
            }
        },

        CategoryEnum.INTAKE: {

            SubCategoryEnum.AIR_FILTERS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'airintake',
                    'airfilter',
                },
            }

        },

        CategoryEnum.RACEWEAR: {

            SubCategoryEnum.BOOTS: {
                MatchMode.KEYWORDS: {
                    'boots',
                    'boot',
                },
                MatchMode.SUBSTRINGS: {

                },
            },

            SubCategoryEnum.CLOTHING: {
                MatchMode.KEYWORDS: {
                    'socks',
                    'underwear',
                    'pants',
                    'shirt',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.GLOVES: {
                MatchMode.KEYWORDS: {
                    'hands',
                    'gloves',
                },
                MatchMode.SUBSTRINGS: {

                },
            },

            SubCategoryEnum.HELMETS: {
                MatchMode.KEYWORDS: {
                    'helmet',
                    'helmets',
                },
                MatchMode.SUBSTRINGS: {

                },
            },
            SubCategoryEnum.SUITS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                },
            },
        },

        CategoryEnum.SUSPENSION: {

            SubCategoryEnum.BAR_BUSHINGS: {
                MatchMode.KEYWORDS: {
                    'bushing',
                    'bushings',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.SHOCK_ABSORBERS: {
                MatchMode.KEYWORDS: {
                    'shock',
                    'absorber',
                },
                MatchMode.SUBSTRINGS: {
                    'shockabsorber',
                },

            },

            SubCategoryEnum.SPRINGS: {
                MatchMode.KEYWORDS: {
                    'springs',
                    'spring',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.STRUTS: {
                MatchMode.KEYWORDS: {
                    'struts',
                },
                MatchMode.SUBSTRINGS: {
                    'strutcartridge',
                    'suspensionstrut',
                },

            },

            SubCategoryEnum.SWAY_BARS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'antiroll',
                    'swaybar',
                },

            },

        },

        CategoryEnum.TIRES: {

            SubCategoryEnum.TIRES_ALL_SEASON: {
                MatchMode.KEYWORDS: {
                    
                },
                MatchMode.SUBSTRINGS: {
                    'allseason',
                },

            },

            SubCategoryEnum.TIRES_ALL_WEATHER: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'allweather',
                },

            },

            SubCategoryEnum.TIRES_ALL_TERRAIN: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'allterrain',
                }
            },

            SubCategoryEnum.TIRES_MUD: {
                MatchMode.KEYWORDS: {
                    'mud',
                    'muddy',
                },
                MatchMode.SUBSTRINGS: {

                }
            },

            SubCategoryEnum.TIRES_SUMMER: {
                MatchMode.KEYWORDS: {
                    'summer',
                },
                MatchMode.SUBSTRINGS: {

                },
            },

            SubCategoryEnum.TIRES_WINTER: {
                MatchMode.KEYWORDS: {
                    'winter',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

        },

        CategoryEnum.TIRE_ACCESSORIES: {

            SubCategoryEnum.TIRES_MISC: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.TIRES_STUDS: {
                MatchMode.KEYWORDS: {
                    'studs'
                },
                MatchMode.SUBSTRINGS: {
                    'tirestud',
                },

            },

            SubCategoryEnum.TIRES_VALVES: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'snapinvalve',
                    'innermountvalve',
                    'innermount45valve',
                    'outermountvalve',
                    'flushmountvalve',
                    'valvecap',
                },
            },

            SubCategoryEnum.TPMS: {
                MatchMode.KEYWORDS: {
                    'tpms',
                },
                MatchMode.SUBSTRINGS: {
                    'tirepressuremonitor',
                },

            },

        },

        CategoryEnum.WHEELS: {
            SubCategoryEnum.WHEELS_AUTOMOTIVE: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                }
            },

            SubCategoryEnum.WHEELS_UTV_ATV: {
                MatchMode.KEYWORDS: {
                    'utv',
                    'atv',
                },
                MatchMode.SUBSTRINGS: {
                    'allterrainvehicle',
                    'utilitytaskvehicle',
                },
            },
        },

        CategoryEnum.WHEEL_ACCESSORIES: {

            SubCategoryEnum.WHEEL_ADAPTERS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'wheeladapter'
                },

            },

            SubCategoryEnum.WHEEL_CAPS: {
                MatchMode.KEYWORDS: {
                    'hubcap',
                    'hubcaps',
                },
                MatchMode.SUBSTRINGS: {
                    'hubcap',
                    'wheelcap',
                    'derbycap',
                },

            },

            SubCategoryEnum.WHEEL_HUB_RINGS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'hubring',
                    'hubcentricring',
                },

            },

            SubCategoryEnum.WHEEL_MISC: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.WHEEL_NUTS_BOLTS: {
                MatchMode.KEYWORDS: {
                    'spline',
                    'hex',
                    'acorn',
                },
                MatchMode.SUBSTRINGS: {
                    'socketadapter',
                    'lockkey',
                    'hexwithkey',
                    'acornnut',
                    'blacknut',
                    'chromenut',
                    'allenkey',
                    'zinckey',
                },

            },

            SubCategoryEnum.WHEEL_RIVETS: {
                MatchMode.KEYWORDS: {
                    'rivet',
                    'rivets',
                },
                MatchMode.SUBSTRINGS: {

                },

            },

            SubCategoryEnum.WHEEL_SPACERS: {
                MatchMode.KEYWORDS: {

                },
                MatchMode.SUBSTRINGS: {
                    'wheelspacer',
                },

            },
        },
    }
