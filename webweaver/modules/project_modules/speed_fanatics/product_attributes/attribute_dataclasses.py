from dataclasses import dataclass, field


class WheelAttributeData:

    def __init__(self):
        self.diameter = None   
        self.width = None   
        self.centerbore = None
        self.bolt_pattern = None
        self.finish = None
        self.load_rating = None
        self.weight = None
        self.backspacing = None
        self.offset = None


class TireAttributeData:

    def __init__(self):
        self.width = None            
        self.aspect_ratio = None    
        self.wheel_diameter = None 
        self.load_index = None   
        self.load_index_dual = None
        self.speed_rating = None
        self.load_description = None
        self.utqg = None          
        self.overall_diameter = None
        self.studdable = None    
        self.service_type = None
