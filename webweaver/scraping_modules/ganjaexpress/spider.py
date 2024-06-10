from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.spider_page import SpiderPage

class GanjaExpressSelectors:
    # Index page:
    products_container = ".shop-container"
    products = ".shop-container .product-small.box"
    product_page_links = ".shop-container .product-small.box .image-fade_in_back a"
    # Single product page
    select_element = "select"
    product_name = "h1.product-title"
    description = ".product-short-description"
    thc_content = ".product-info > p.uppercase"
    single_price = ".product-page-price"
    product_variations_select = "#pa_amount"
    product_variations_options = "#pa_amount > option"
    variation_price = ".variations_form.cart span.price > span.woocommerce-Price-amount > bdi"
    # Review
    review_score = ".product-info strong.review"
    review_count = ".product-info span.review"


class GanjaExpressSpider(PlaywrightSpider):

    selectors = GanjaExpressSelectors

    def __init__(self, spider_id:int, domain:str, **kwargs):
        super().__init__(spider_id, domain, **kwargs)
        # self.url = "https://www.ganjaexpress.to/shop/"
        self.url = "https://www.ganjaexpress.to/product-category/marijuana-edibles/"


    async def run(self):
        await self.start('chromium', headless=True)

        context = await self.new_context()
        spider_page = await self.new_page(context.context)
        res = await spider_page.goto(self.url)
        if res is None:
            return

        page = spider_page.page

        while True:
            await page.wait_for_load_state(state='load', timeout=10000)
            await page.wait_for_selector(self.selectors.products_container)
            product_links = await page.query_selector_all(self.selectors.product_page_links)
            for product_link in product_links:
                new_spider_page = await self.new_page(context.context)
                await new_spider_page.goto(await product_link.get_attribute('href'))
                await new_spider_page.page.wait_for_load_state(state='load')
                page_data = await self.product_page(new_spider_page)
                await new_spider_page.page.close()
                await self.random_delay(1, 3)

                data = {
                    'product': {
                        'product_name': ...,
                        'single_price': ...,
                        'variations': [
                            
                        ],
                        'thc_content': ...,
                    },
                    'review': {
                        'review_count': ...,
                        'review_score': ...
                    }
                }


            break


    async def product_page(self, spider_page:SpiderPage):

        page = spider_page.page
        await page.wait_for_load_state(state='load', timeout=10000)
        variations_select = await spider_page.check_element(self.selectors.product_variations_select)
        select_element = await spider_page.page.query_selector('.product-info select')
        if select_element:
            product_name = await page.query_selector(self.selectors.product_name)
            print('variations: ', await product_name.text_content())
            print()
        else:
            soup = self.get_soup(markup=await page.inner_html('.product-main'))
            product_name = soup.select_one(self.selectors.product_name)
            price = soup.select_one(self.selectors.single_price)
            print(product_name.text)
            print(price.text)
            print()
