from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.soup_base import SpiderSoup


class AutoEvolutionSelectors:
    vehicle_makes = '.carlist > .carman'

    # vehicle make row
    models_link = 'a:first-of-type'
    make_name = 'h5 span'

    # models page
    vehicle_models = '.carmodels > .carmod'
    model_name = 'h4'


class AutoEvolutionSpider(PlaywrightSpider):

    selectors = AutoEvolutionSelectors

    def __init__(self, spider_asset: SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = 'https://www.autoevolution.com/cars/'

    def scrape_models(self, models_soup: SpiderSoup, make_name: str) -> list[str]:
        models = []
        vehicle_models = models_soup.select(self.selectors.vehicle_models)
        for vehicle_model in vehicle_models:
            model_name = vehicle_model.select_one(
                self.selectors.model_name).text
            if model_name.startswith(make_name):
                model_name = model_name.replace(make_name, '')
            models.append(model_name.strip())
        return models

    async def run(self):
        res = await self.aio.get(self.url, use_proxy=True)
        if res.status != 200:
            raise self.errors.SpiderHttpError(
                f"Status code: {res.status}, Url: {self.url}")

        soup = self.get_soup(await res.text())
        vehicle_makes = soup.select(self.selectors.vehicle_makes)
        self.shuffle(vehicle_makes)
        for vehicle_make in vehicle_makes:
            make_name = vehicle_make.select_one(self.selectors.make_name).text
            models_link = vehicle_make.select_one(
                self.selectors.models_link)['href']
            await self.jitter(0.2, 1)
            res_models = await self.aio.get(models_link, use_proxy=True)
            if res_models.status != 200:
                raise self.errors.SpiderHttpError(
                    f"Status code: {res_models.status}, Url: {models_link}")
            models_soup = self.get_soup(await res_models.text())
            models = self.scrape_models(models_soup, make_name)

            for model in models:
                yield {
                    'vehicle_make': make_name,
                    'vehicle_model': model
                }
