from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.soup_base import SpiderTag
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider


class KelleyBlueBookSelectors:
    
    table_rows = 'tbody.css-ap66tw.ee33uo34 > tr'
    model = 'td:nth-of-type(2)'
    make = 'td:nth-of-type(3)'


class KelleyBlueBookSpider(PlaywrightSpider):

    selectors = KelleyBlueBookSelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.urls = [
            'https://www.kbb.com/car-make-model-list/used/view-all/model/',
            'https://www.kbb.com/car-make-model-list/new/view-all/model/',
        ]



    def scrape_row(self, table_row:SpiderTag) -> dict[str, str]:
        return {
            'vehicle_make': table_row.select_one(self.selectors.make).text.strip(),
            'vehicle_model': table_row.select_one(self.selectors.model).text.strip(),
        }


    async def get_listings(self, url:str) -> str:
        """Fetch the page which contains the table of car makes/models."""
        res = await self.aio.get(url, use_proxy=False)
        if res.status == 200:
            return await res.text()
        raise self.errors.SpiderHttpError(f"HTTP code{res.status}: {url}")



    # async def compare_used_to_new(self):
    #     """Quick test to see if there is overlap in used/new pages."""


    async def run(self):
        for url in self.urls:
            soup = self.get_soup(await self.get_listings(url))
            table_rows = soup.select(self.selectors.table_rows)
            for table_row in table_rows:
                data = self.scrape_row(table_row)
                # self.jitter(0.5, 1)
                yield data

