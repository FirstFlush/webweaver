from webweaver.webscraping.fuzzy_matching.fuzzy_handler import FuzzyHandler


class SpiderFuzzer:
    """This class serves as the spider's means of creating a FuzzyHandler
    object.
    """
    @classmethod
    async def get_handler_from_model(cls, model, field_name:str) -> FuzzyHandler:    
        return await FuzzyHandler.get_handler_from_model(
            model=model, 
            field_name=field_name
        )


    @staticmethod
    def get_handler(data_set:list[str], preprocess:bool=True) -> FuzzyHandler:
        return FuzzyHandler(
            data_set=data_set, 
            model_map=None, 
            preprocess=preprocess
        )
    

    @staticmethod
    def preprocess(s:str) -> str:
        return FuzzyHandler.preprocess(s, pattern=FuzzyHandler.REGEX_PATTERNS.preprocess)
    
