from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider


class BCBudSupplySelectors:

    #homepage
    categories = '#wide-nav a.nav-top-link'
    #product index page
    product = '.product-small.box'
    #product display page



class BCBudSupplySpider(PlaywrightSpider):

    selectors = BCBudSupplySelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = spider_asset.domain

    async def run(self):
        await self.start('chromium', headless=True)
        spider_context = await self.new_context()
        spider_page = await spider_context.new_spider_page()
        res = await spider_page.goto_or_none(self.url)
        if res is None:
            return
