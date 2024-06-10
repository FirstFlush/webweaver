from webweaver.modules.project_modules.speed_fanatics.categorization.base_handler import BaseHandler


class VehicleHandler(BaseHandler):
    """Attempts to determine car makes/models from a set of strings.
    The VehicleHandler will only consider a vehicle matched if both the 
    make AND model is matched independently in any of the strings.
    
    strings:list[str] this param is a list of whatever strings need to be parsed
    from the page. examples would be product name, product description, variationtype,
    brand_name, or any other bit of text scraped from the page that could be relevant
    in determining the makes/models the product applies to.

    Biggest concern: Avoid false positives!
    Vehicle make "Smart" creates a model called "1". how do we parse a string
    and avoid matching false positives on Smart and 1?
    """




