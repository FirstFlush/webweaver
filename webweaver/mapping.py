# These classes provide a mapping for routes & templates in order to make
# code less error prone and more reusable.

class RouteMap:
    DOMAIN = "http://localhost:8000"
    CHOOSE_CAMPAIGN_SPIDERS = "/campaigns/choose_spiders"
    CHOOSE_CAMPAIGN_PARAMS = "/campaigns/choose_params"
    CONFIRM_CAMPAIGN = "/campaigns/confirm"
    LIST_PARAMS = "/campaigns/list_params"

    CREATE_SPIDER = "/scrape/create_spider"
    CREATE_PARAMS = "/scrape/create_params"
    LAUNCH_CAMPAIGN = "/scrape/launch_campaign"
    LAUNCH_SPIDER = "/scrape/launch_spider"
    SAVE_JOB_TO_FILE = "/scrape/jobs/save"

    SPEED_FANATICS_PRODUCTS = "/speed_fanatics/products/"
    SPEED_FANATICS_SEARCH = "/speed_fanatics/search"


class TemplateMap:
    # TEMPLATE_DIR = "frontend/templates/"
    CHOOSE_CAMPAIGN_SPIDERS = "campaigns/choose_spiders.html.j2"
    CHOOSE_CAMPAIGN_PARAMS = "campaigns/choose_params.html.j2"
    CONFIRM_CAMPAIGN = "campaigns/confirm_campaign.html.j2"

    SPEED_FANATICS_PRODUCTS = "speed_fanatics/products.html.j2"
    SPEED_FANATICS_PDP = "speed_fanatics/pdp.html.j2"
