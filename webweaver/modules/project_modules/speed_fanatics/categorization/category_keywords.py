from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    CategoryEnum, 
    SubCategoryEnum,
    MatchMode
)
from enum import Enum



class CategoryKeyWords:
    """These are keywords to be searched for/matched BEFORE 
    we try any fuzzy-matching or fuzzy preprocessing

    First we loop through the keywords to see if there are any exact matches,
    then we search substrings.

    """

    categories = {
        CategoryEnum.AUTOBODY : {
            MatchMode.KEYWORDS : {
                'spoiler',
                'diffuser',
                'dashboard',
                'skirt',
            },
            MatchMode.SUBSTRINGS : {

            }
        },

        CategoryEnum.BRAKES : {
            MatchMode.KEYWORDS : {
            'brakes',
            'brake',
            'brake-kit',
            'brake-kits',
            'brake-pad',
            'brake-pads',
            'brake-bundle'
            'brake-bundles'
            'master-cylinder',
            
            
            },
            MatchMode.SUBSTRINGS : {
            'jhook',
            'mastercylinder',
            },
        },
        

        CategoryEnum.EXHAUST : {
            MatchMode.KEYWORDS : {
                'exhaust',
                'exhaust-kit',
                'exhaust-kits',
            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        CategoryEnum.INTAKE : {
            MatchMode.KEYWORDS : {
                'intake',
                'cold-air',
            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        CategoryEnum.RACEWEAR : {
            MatchMode.KEYWORDS : {
                'clothing',
                'socks',
                'underwear',
                'helmet',
                'gloves',
                'suit',
                'jacket',
            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        CategoryEnum.SUSPENSION : {
            MatchMode.KEYWORDS : {
                'suspension',
                'springs',
            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        CategoryEnum.TIRES : {
            MatchMode.KEYWORDS : {
            
            },
            MatchMode.SUBSTRINGS : {
                
            }

        },
        
        CategoryEnum.TIRE_ACCESSORIES : {
            MatchMode.KEYWORDS : {
                'tpms',
            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        CategoryEnum.WHEELS : {
            MatchMode.KEYWORDS : {

            },
            MatchMode.SUBSTRINGS : {
                
            }
        },
        CategoryEnum.WHEEL_ACCESSORIES : {
            MatchMode.KEYWORDS : {

            },
            MatchMode.SUBSTRINGS : {

            }
        },
        
        # CategoryEnum.UNKNOWN : {

        # },
        

    }







    # keyword_sets = {
    #     CategoryEnum.AUTOBODY : {
    #         'spoiler',
    #         'diffuser',
    #         'dashboard',
    #         'skirt',
    #     },

    #     CategoryEnum.BRAKES : {
    #         'brakes',
    #         'brake',
    #         'brake-kit',
    #         'brake-kits',
    #         'brake-pad',
    #         'brake-pads',
    #         'brake-bundle'
    #         'brake-bundles'
    #         'master-cylinder',
    #         'master cylinder'
    #         'j hook',

    #     },
        

    #     CategoryEnum.EXHAUST : {
    #         'exhaust',
    #         'exhaust-kit',
    #         'exhaust-kits',
    #     },
        
    #     CategoryEnum.INTAKE : {
    #         'intake',
    #         'cold-air',
            
    #     },
        
    #     CategoryEnum.RACEWEAR : {
    #         'clothing',
    #         'socks',
    #         'underwear',
    #         'helmet',
    #         'gloves',
    #         'suit',
    #         'jacket',
    #     },
        
    #     CategoryEnum.SUSPENSION : {
    #         'suspension',
    #         'springs',
    #     },
        
    #     CategoryEnum.TIRES : {

    #     },
        
    #     CategoryEnum.TIRE_ACCESSORIES : {
    #         'tpms',
    #     },
        
    #     CategoryEnum.WHEELS : {

    #     },
        
    #     CategoryEnum.WHEEL_ACCESSORIES : {

    #     },
        
    #     # CategoryEnum.UNKNOWN : {

    #     # },
        

    # }

