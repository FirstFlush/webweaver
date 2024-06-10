import asyncio
import logging
from fastapi import HTTPException

from webweaver.exceptions import CampaignBuilderError
from webweaver.project.models import Project
from webweaver.webscraping.middleware.middleware_manager import MiddlewareManager
from webweaver.webscraping.pipelines.pipeline_listener import PipelineListener
from webweaver.webscraping.proxy.proxy_manager import ProxyManager
from webweaver.schema.pydantic_schemas import LaunchSpiderSchema, LaunchCampaignSchema
from webweaver.webscraping.registry.builders import CampaignBuilder, SoloSpiderBuilder
from webweaver.webscraping.registry.scraping_registry import scraping_registry
from webweaver.webscraping.spiders.spider_launcher import SpiderLauncher


logger = logging.getLogger('scraping')


class WebScrape:
    """Class for any scraping-related views/routes. Mainly created to keep
    route files clean and standardize the logic between launching spiders
    and launching campaigns.
    """
    async def scrape(
        self, 
        launch_data:LaunchSpiderSchema|LaunchCampaignSchema,
        is_proxy:bool=True,
        is_campaign:bool=False,
        project_id:int|None = None,
    ):

        # Initialize middleware
        middleware_manager = MiddlewareManager()
        middleware_manager_interface = middleware_manager.spider_middleware_manager_interface
        logger.debug(f'SpiderMiddlewareManagerInterface: {middleware_manager_interface}')

        # Initialize proxy
        if is_proxy:
            proxy_manager = ProxyManager()
            proxy_manager_interface = proxy_manager.spider_manager_interface
        else:
            proxy_manager_interface = None
        logger.debug(f'ProxyManagerInterface: {proxy_manager_interface}')


        # Intialize scraping registry
        if is_campaign:
            try:
                builder = await CampaignBuilder.build_campaign(launch_data)
            except CampaignBuilderError:
                raise HTTPException(status_code=404, detail="Could not launch campaign with information provided.")
            await scraping_registry.build(campaign_builder=builder)
        else:
            builder = SoloSpiderBuilder(launch_data)
            await builder.initialize_solo_scrape()
            await scraping_registry.build(solospider_builder=builder)
        logger.info('Scraping registry built')
        logger.info(f"Tables: {', '.join(sorted(scraping_registry.scrape_table_names))}")
        logger.debug(f'Table instances: {scraping_registry.scrape_table_models}')

        # Initialize Project, if required
        project_id = 3 # speed fanatics
        # project_id = None
        if project_id:
            project = await Project.get(id=project_id)
            project_handler_class = project.get_handler()
            project_handler = project_handler_class()
            await project_handler.initialize_project()
            
            # for brand_str, brand in project_handler.brand_name_to_brand.items():
            #     print(brand_str, " : ", brand.brand_name)
            # exit(0)

            logger.info(f"ProjectHandler initialized for {project.project_name} project.")
            logger.debug(f"ProjectHandler: {project_handler}")
            # print('fuzzy handler in webscrape: ', project_handler.fuzzy_handler)
            # print('project_handler in webscrape: ', project_handler)
        else:
            project_handler = None


        queue = asyncio.Queue()
        logger.debug('Async Queue object created')
        sl = SpiderLauncher(
            queue, 
            scraping_registry.spiders,
            middleware_manager_interface=middleware_manager_interface,
            proxy_manager_interface=proxy_manager_interface
        )
        logger.debug('Initialized Spider Launcher')
        pl = PipelineListener(queue, project_handler=project_handler)
        logger.debug('Initialized Pipeline Listener')

        await asyncio.gather(sl.launch(), pl.listen())

        await scraping_registry.finish()
        if project_handler:
            project_handler.finish()