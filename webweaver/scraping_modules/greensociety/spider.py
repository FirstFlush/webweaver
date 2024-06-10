
import asyncio
from bs4 import NavigableString, Tag, ResultSet
from pathlib import Path
from playwright.async_api import Page, ElementHandle
import sys
from tortoise.exceptions import OperationalError
from typing import TYPE_CHECKING

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.soup_base import SpiderSoup, SpiderTag
from webweaver.webscraping.spiders.spider_page import SpiderPage
from webweaver.modules.project_modules.dispensaries.weed_spider import WeedSpiderMixin
from webweaver.modules.project_modules.dispensaries.mapping.category_enums import CategoryEnum, SubCategoryEnum
from webweaver.modules.project_modules.dispensaries.data.strains.models import Strain
from webweaver.modules.project_modules.dispensaries.data.products.models import ProductDescription

if TYPE_CHECKING:
    import io


class GreenSocietySelectors:

    footer = '#footer'
    close_modal = 'button.needsclick.klaviyo-close-form'
    products_container = '.shop-container'
    product_card = 'div.product-small.box'
    product_links = 'div.product-small.box .box-image a'
    product_name = '.name.product-title'
    category = '.title-wrapper'
    hidden = '.hidden' # for decomposing unwated elements in the tree
    variations = '.ux-swatches-fake'
    price_container = '.price'
    price = '.price .woocommerce-Price-currencySymbol' # Take the parent of this element
    deleted_price = 'del'
    pdp_link = 'a' # select from within product_card

    # pdp page:
    description_paragraphs = '#tab-description > p'


class GreenSocietySpider(PlaywrightSpider, WeedSpiderMixin):

    selectors = GreenSocietySelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.semaphore = asyncio.Semaphore(5)
        self.product_name_to_pdp_link = {}
        # self.url = self.params['start_url']
        # self.url = 'https://greensociety.cc/product-category/edibles/'
        self.url = 'https://greensociety.cc/product-category/all-products/'
        # self.url = 'https://greensociety.cc/product-category/green-room/'


    async def run(self):

        # print('fuzzy handler: ', self.project_handler.fuzzy_handler)
        # print('dispensary registry: ', self.project_handler.dispensary_registry)
        # print('project_handler: ', self.project_handler)
        self.fuzzy_handler = await self.fuzzing.get_handler_from_model(model=Strain, field_name='name')

        await self.start('chromium', headless=True)
        spider_context = await self.new_context()
        spider_page = await spider_context.new_spider_page()
        page = spider_page.page
        res = await spider_page.goto_or_none(self.url)
        if res is None:
            yield {}

        await page.wait_for_load_state(state='load', timeout=50000)
        # await spider_page.infinite_scroll2(
        #     self.selectors.footer, 
        #     timeout=10000, 
        # )
        # await self.click_modal(page)

        product_cards = await page.query_selector_all(self.selectors.product_card)
        print('product cards length: ', len(product_cards))

        file = self.stdout_to_file('std_to_file__wratio.txt')

        tasks = [self.scrape_card(product_card) for product_card in product_cards]
        await asyncio.gather(*tasks)

        self.stdout_to_file_close(file)


        yield {'stuff':'bleh'}


    async def scrape_card(self, product_card_element:ElementHandle) -> dict:
        """Use BeautifulSoup to scrape the product data"""
        async with self.semaphore:
            soup = self.get_soup(await product_card_element.inner_html())
            product_name = soup.select_one_text(self.selectors.product_name)
            if not product_name:
                self.log("Product name not found in GreenSociety spider's scrape_card(). Skipping...")
                return {}

            category_element = soup.select_one(self.selectors.category)
            category_text = self._get_category_text(category_element)
            category_enum, subcategory_enum = self.get_categories(
                category_text = category_text,
                product_name = product_name,
            )

            print(product_name)
            variations = self.get_variations(soup=soup)
            print('variations: ')
            print(variations)

            if not variations:
                prices = self.get_prices(soup)
                print('prices:')
                print(prices)
            print(category_text)
            print(category_enum, subcategory_enum)
            # if category_enum == CategoryEnum.FLOWER or subcategory_enum == SubCategoryEnum.BULK_FLOWER:
            #     description = await self.get_description(product_card_element)
            #     try:
            #         await ProductDescription.create(
            #             product_name = product_name,
            #             text = description
            #         )
            #     except OperationalError:
            #         pass
            print('------------------------')
            print()

    def _get_category_text(self, category_element:Tag) -> str:
        for item in category_element.contents:
            if type(item) == NavigableString and len(item.text.strip()) > 0:
                return item.text.strip()

    def _get_category_enum(self, category_text:str, product_text:str=None) -> CategoryEnum:
        return self.get_category(category_text, product_text)


    def get_price(self, soup:SpiderSoup) -> str | None:
        """Gets the price and/or price range. This does not get 
        variation prices though. That is handled in get_variations.
        """
        price_container_element:SpiderTag = soup.select_one(self.selectors.price_container)
        if price_container_element:
            price_container_element.select_and_decompose(self.selectors.deleted_price)
            price_element = price_container_element.select_one(self.selectors.price)
            return price_element.parent.text if price_element else None
        return None


    def get_prices(self, soup:SpiderSoup) -> list[str] | None:
        """This method returns a list of all prices found.
        
        There should be at min 1 price and and max 2 prices, based on the dispensary's HTML.
        *Anything else is a problem
        """
        prices = []
        price_container_element:SpiderTag = soup.select_one(self.selectors.price_container)
        if price_container_element:
            price_container_element.select_and_decompose(self.selectors.deleted_price)
            price_elements = price_container_element.select(self.selectors.price)
            for price_element in price_elements:
                prices.append(price_element.parent.text)
        return prices






    def get_variations(self, soup:SpiderSoup) -> list[dict]:
        """If variations found, this will return a dict 
        containing VariationEnums and variation price
        """
        variations_list = []
        variations = soup.select_one(self.selectors.variations)
        if variations:
            for variation in variations.children:
                if not hasattr(variation, 'get'):
                    continue
                variation_value = variation.get('data-value')
                variation_price = variation.get('data-price')
                if variation_value:
                    # print('VariationEnum: ', self.get_variation_enum(variation_value))
                    variation_enum = self.get_variation_enum(variation_value)
                    variations_list.append({
                        'variation_enum': variation_enum,
                        'variation_price': variation_price
                    })

        return variations_list


    async def click_modal(self, page:Page):
        close_button = await page.query_selector(self.selectors.close_modal)
        if close_button:
            print('close button: ', close_button)
            await close_button.click()


    async def get_description(self, product_card:ElementHandle) -> str | None:
        """Clink the PDP link for each product and scrape the description text."""
        await self.jitter(1, 4)
        link_element = await product_card.query_selector(self.selectors.pdp_link)
        try:
            link = await link_element.get_attribute('href')
        except AttributeError as e:
            self.log(e)
            return
        
        spider_context = await self.new_context(stateful=False)
        spider_page = await spider_context.new_spider_page()
        await spider_page.goto_or_none(link)
        await spider_page.page.wait_for_load_state(state='load', timeout=100000)
        soup = self.get_soup(markup=await spider_page.page.inner_html('body'))
        paragraphs = [ el.text for el in soup.select(self.selectors.description_paragraphs)]
        await spider_page.page.close()
        return'\n'.join(paragraphs)














    def stdout_to_file(self, file_name:str=None) -> "io.TextIOWrapper":
        # file = open('std_to_file_edibles.txt', 'w')
        if not file_name:
            file_name = f"{self.spider_asset.spider_name}__std_to_file.txt"
        file = open(file_name, 'w')
        sys.stdout = file
        return file


    def stdout_to_file_close(self, file:"io.TextIOWrapper"):
        sys.stdout = sys.__stdout__
        file.close()



# data = {
#     'product_name': str,
#     'category': str|None,
#     'subcategory': str|None,
#     'single_price': float|None,
#     'range_price': str|None,        # $140.00 - $180.00
#     'variations': [
#         {
#             'variation_name': str,
#             'variation_price': float|None,
#         }
#     ]
# }
        



















    # def scrape_product(self, soup:SpiderSoup) -> dict[str,str]:
    #     category_element = soup.select_one(self.selectors.category)

    #     for item in category_element.contents:
    #         if type(item) == NavigableString and len(item.text.strip()) > 0:
    #             category = item.text.strip()
    #             print("Category: ", category)
    #             category_enum = self.get_category(category)
    #             print("My category: ", category_enum.value)
    #             print("My Subcategory: ", self.get_subcategory(category_enum))
    #     print('-------------------------------')
    #     print()




    # def scrape_bundle(self, soup:SpiderSoup):
    #     category_element = soup.select_one(self.selectors.category)
    #     # print(category_element.contents)
    #     for item in category_element.contents:
    #         if type(item) == NavigableString and len(item.text.strip()) > 0:
    #             category = item.text.strip()
    #             print("Category: ", category)
    #             print("My category: ", self.get_category(category).value)
    #     print('-------------------------------')
    #     print()
        












            # await self.jitter()
    # async def scrape_card(self, product_card_element:ElementHandle) -> dict:
    #     """Use BeautifulSoup to scrape the product data"""
    #     soup = self.get_soup(await product_card_element.inner_html())
    #     product_name = soup.select_one_text(self.selectors.product_name)
    #     if not product_name:
    #         self.log('Product name not found. Skipping...')
    #         return {}
        
    #     category_element = soup.select_one(self.selectors.category)
    #     category_text = self._get_category_text(category_element)
    #     category_enum = self._get_category_enum(category_text, product_name)
    #     print('product name: ', product_name)
    #     print('category text: ', category_text)
    #     print('CategoryEnum: ', category_enum)
    #     try:
    #         subcategory_enum = self.get_subcategory(category_enum, product_name, category_text)
    #         print('SubcategoryEnum: ',subcategory_enum)
    #     except KeyError as e:
    #         subcategory_enum = None
    #         print(e)
    #         # print(f"key error on {product_name}")
    #     except AttributeError as e:
    #         subcategory_enum = None
    #         print("AttributeError!!")
    #         pass
    #     variations = self.get_variations(soup=soup)
    #     if variations:
    #         print(variations)
    #     # price = self.get_price(soup)
    #     prices = self.get_prices(soup)

    #     price = None
    #     price_range = None
    #     if len(prices) == 1:
    #         price = prices[0]
    #     elif len(prices) == 2:
    #         price_range = prices
    #     else:
    #         raise IndexError(f"{self.spider_asset.spider_name} prices returned length of {len(prices)}")


    #     print('Price: ,', price)
    #     print('Price Range: ', price_range)
    #     # if category_enum == CategoryEnum.FLOWER:
    #     # print(f"{self.fuzzing.preprocess(product_name)}")
    #     # print(self.fuzzy_handler.best_match(product_name))
    #     if category_enum == CategoryEnum.FLOWER:
    #         print(self.check_strain(product_name))
    #     print('Category Model: ', self.project_handler.dispensary_registry.category_enum_to_model.get('category_enum'))
    #     print('SubCategory Model: ', self.project_handler.dispensary_registry.subcategory_enum_to_model.get('subcategory_enum'))
    #     # print(self.fuzzy_handler.best_match(self.fuzzing.preprocess(product_name).strip()))

    #     print()
    #     print()
    #     # {
    #     #     'product_name': product_name.strip(),
    #     #     'price': ...,
    #     #     'price_range': ...,
    #     #     'category': category_enum,
    #     #     'subcategory': subcategory_enum,
    #     #     'variations': variations,
    #     # }


