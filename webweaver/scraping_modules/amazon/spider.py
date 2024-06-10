from playwright.async_api import Page, ElementHandle
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
# from webscraping.spiders.spider_page import SpiderPage


class AmazonSelectors:
    # main page
    search_input = '#twotabsearchtextbox'
    search_input2 = '#nav-bb-search'

    #search results
    results_container = '.s-main-slot'
    results = '.s-main-slot .s-widget-container.s-spacing-small, .a-carousel > li'
    
    #in result cart
    price = '.a-price > span:nth-of-type(2)'


class AmazonSpider(PlaywrightSpider):

    selectors = AmazonSelectors

    def __init__(self, spider_asset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.search_query = "coffee machine"


    async def get_search_input(self, page:Page) -> ElementHandle:
        """Search <input> on main page loads with different id values. Sneaky lol"""
        search_input = await page.query_selector(self.selectors.search_input)
        if search_input is None:
            search_input = await page.query_selector(self.selectors.search_input2)
        return search_input
    

    async def run(self):
        await self.start('firefox', headless=False)
        context = await self.new_context()
        spider_page = await self.new_page(context.context)
        page = spider_page.page
        res = await spider_page.goto_or_none(self.url)
        if res is None:
            return
        await page.wait_for_load_state(state='load')
        search_input = await self.get_search_input(page)
        await search_input.fill(self.search_query)
        await search_input.press('Enter')
        await self.random_delay(3, 4)
        await page.wait_for_load_state(state='load')
        results_container = await page.wait_for_selector(self.selectors.results_container)
        results = await page.query_selector_all(self.selectors.results)
        print('results: ', len(results))


        for i, result in enumerate(results):
            try:
                price = await result.query_selector(self.selectors.price)
                print(i+1, await price.text_content())
            except AttributeError:
                continue

        await self.random_delay(1000, 2000)