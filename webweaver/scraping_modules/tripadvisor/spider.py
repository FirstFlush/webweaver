from webscraping.spiders.models import SpiderAsset
from webscraping.spiders.spider_base import PlaywrightSpider


class TripAdvisorSelectors:
    ...


class TripAdvisorSpider(PlaywrightSpider):

    selectors = TripAdvisorSelectors

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
