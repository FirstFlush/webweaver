from typing import TYPE_CHECKING
from webweaver.modules.project_modules.dispensaries.weed_project_handler import WeedProjectHandler
from webweaver.modules.project_modules.speed_fanatics.speed_project_handler import SpeedProjectHandler

if TYPE_CHECKING:
    from webweaver.project.project_base import ProjectHandler



# mapping of Project IDs to their respective handler class
# This mapping design is preferred over a dynamic-loading design (as with 
# SpiderAsset grabbing its respective Spider class) due to the fact that
# new projects will not be started as frequently as new Spiders, and this 
# is a simple 1-time thing for each new project. 

PROJECT_HANDLER_MAP:dict[int, "ProjectHandler"] = {
    1: WeedProjectHandler,
    3: SpeedProjectHandler,
}