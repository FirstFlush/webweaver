



class SpeedKeyWords:
    """Key words to automatically map products to their respective Category/SubCategory Enum"""
    pass_product = {
        'gift card',
        'video',
        't-shirt',
    }

    # Used when matching brand in speed_pipeline
    # brand_ignore = {
    #     'tires',
    #     'products',
    #     'wheels',
    #     'and',
    #     'company',
    #     'parts',
    # }


    @staticmethod
    def remove_keywords(s:str, keywords:set) -> str:
        return ' '.join([word for word in s.split() if word not in keywords])

    
    # @classmethod
    # def remove_brand_keywords(cls, brand_name:str) -> str:
    #     """Strip the keywords out of the brand name"""
    #     return cls.remove_keywords(brand_name, cls.brand_ignore)