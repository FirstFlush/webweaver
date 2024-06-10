import asyncio

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.soup_base import SpiderSoup, SpiderTag
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
from webweaver.modules.project_modules.speed_fanatics.speed_enums import AddOnEnum


class SoulPPSelectors:
    
    product_cards = '.products .products-inner'
    dead_link = 'h1'

    # product card:
    product_name = 'p'
    prices = '.price .woocommerce-Price-currencySymbol' 
    price_container = '.price'
    pdp_substring = '/product/' #substring passed to soup.get_href()
    is_vars = '.button.product_type_variable.add_to_cart_button'
    is_on_sale = '.onsale'

    # pdp:
    description_short = '.woocommerce-product-details__short-description'
    description_long = '#tab-description > p'
    add_ons = '.summary.entry-summary .bundled_item_optional'
    variations = '.summary.entry-summary table.variations tr'
    images = '.woocommerce-product-gallery__image img'

    # from add_on element in pdp:
    add_on_name = '.bundled_product_title_inner'
    add_on_detail = '.product_excerpt'
    add_on_price = '.price'

    # from variation in pdp
    variation_type = 'th' # grab from within variations elemenet
    variation_values = 'td > select > option' # grab from within variations element


class SoulPPSpider(PlaywrightSpider, SpeedSpiderMixin):
    """If no price is found in the product card, then the product is 
    discontinued and should be skipped.
    """

    selectors = SoulPPSelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = 'https://soulpp.com/shop-performance-parts/'
        self.brand = {'brand_name' : 'Soul Performance Products'}

    def check_vars(self, variations:list[str], product_name:str, pdp_link:str):
        """SoulPP has an incredibly frustrating way of listing product variations.
        This method is to check if the product has variations or not. I might need
        to do some manual work on those products, if there aren't too many of them.
        """
        if len(variations) >= 2:
            # TESTING: .............................
            with open('soulpp_vars.txt', 'a+') as f:
                f.write(product_name)
                f.write("\n")
                f.write(pdp_link)
                f.write("\n\n")
            # ......................................



    # def scrape_prices(self, product_card:SpiderTag) -> list[dict[str, str]]:
    #     price_elements = product_card.select(self.selectors.prices)
    #     return price_elements


    def is_on_sale(self, product_card:SpiderTag) -> bool:
        return bool(product_card.select_one(self.selectors.is_on_sale))


    def is_old_price(self, price_element:"SpiderTag") -> bool:
        """Checks if any of the parents are <del> elements."""
        return any(parent.name == 'del' for parent in price_element.parents)


    def scrape_prices(self, product_card:"SpiderTag") -> list[dict[str, str]]:
        """This method returns a list of all prices found.
        
        There should be at min 1 price and and max 2 prices, based on the dispensary's HTML.
        *Anything else is a problem
        """
        price_elements:SpiderTag = product_card.select(self.selectors.prices)
        # prices = [price.parent.text for price in price_elements]
        prices = []
        for price_element in price_elements:
            d={}
            d['msrp'] = price_element.parent.text
            if len(price_elements) > 1:
                d['is_old'] = self.is_old_price(price_element)
            prices.append(d)
        return prices


    def scrape_descriptions(self, pdp_soup:SpiderSoup) -> list[str]:
        """Scrapes the two descriptions from the PDP."""
        description_short = pdp_soup.select_one(self.selectors.description_short).text
        description_long_elements = pdp_soup.select(self.selectors.description_long)
        description_long = "\n\n".join([element.text.strip() for element in description_long_elements])
        
        return description_short, description_long



    async def scrape_images(self, pdp_soup:SpiderSoup) -> list[dict[str, bytes]]:
        images = []
        image_elements = pdp_soup.select(self.selectors.images)
        for image_element in image_elements:
            await self.jitter(0.2, 0.5)
            image_binary = await self.aio.scrape_image(image_element, src_attribute='data-src')
            images.append({'image':image_binary})
        return images


    def is_var_bool(self, variation_type_name:str) -> bool:
        """On SoulPP sometimes 'add-ons' are displayed as product variations, 
        but with yes/no as the variation options. I would rather save these as add-ons,
        as the product can still be purchased even when "no" is chosen.
        """
        return bool(variation_type_name.startswith('Add '))


    def scrape_variations_and_addons(self, pdp_soup:SpiderSoup):# -> list[dict[str, str|list[str]]]:
        """Scraping variations & add-ons together in 1 function because some add-ons are presented
        as variations. By scraping both in 1 function I can sort & separate them easier.
        """
        variations = []
        add_ons = []

        variation_elements = pdp_soup.select(self.selectors.variations)
        add_on_elements = pdp_soup.select(self.selectors.add_ons)



        if variation_elements:
            for variation_element in variation_elements:
                variation_type_name = variation_element.select_one(self.selectors.variation_type).text

                # TESTING: .............................
                if self.is_var_bool(variation_type_name):
                    with open('addons_posing_as_vars.txt', 'a+') as f:
                        f.write(pdp_soup.select_one('h1.product_title').text)
                        f.write("\n")
                # ......................................

                variation_values:list[dict[str,str]] = []
                variation_value_elements = variation_element.select(self.selectors.variation_values)
                ignore_value = self.fuzzing.preprocess('Choose an option')
                for variation_value in variation_value_elements:
                    if self.fuzzing.preprocess(variation_value.text) == ignore_value:
                        continue
                    variation_values.append({
                        'value': variation_value.text
                    })
                variation_type_name = variation_type_name[len('Select '):] if variation_type_name.startswith('Select ') else variation_type_name

                variations.append({
                    'variation_type': {
                        'variation_type_name': variation_type_name,
                        'variation_type_enum': self.get_variation_enum_from_text(variation_type_name)
                    },
                    'variation_values': variation_values,
                })

        if add_on_elements:
            for add_on_element in add_on_elements:
                add_on = self.scrape_add_on(add_on_element)
                if add_on:
                    add_ons.append(add_on)

        return variations, add_ons


    def scrape_add_on(self, add_on_element:SpiderTag) -> dict:
        name = add_on_element.select_one(self.selectors.add_on_name)
        detail_element = add_on_element.select_one(self.selectors.add_on_detail)
        detail = detail_element.text if detail_element else None
        price = add_on_element.select_one(self.selectors.add_on_price)

        #Check if its warranty:
        if 'warranty' in self.fuzzing.preprocess(name.text):
            add_on_enum = AddOnEnum.WARRANTY
        else:
            add_on_enum = AddOnEnum.EXTRA_PURCHASE

        return {
            'add_on_enum': add_on_enum,
            'name': name.text,
            'detail': detail,
            'price_modifier': price.text
        }


    async def scrape_product_card(self, product_card:SpiderTag) -> dict|None:
        product_name = product_card.select_one(self.selectors.product_name).text
        prices = self.scrape_prices(product_card)
        is_on_sale = self.is_on_sale(product_card)
        if not prices:  # product is discontinued
            return

        pdp_href = product_card.get_href(substring='/product/')

        await self.jitter(0.5, 5)
        # await self.jitter(1, 3)
        res_pdp = await self.aio.get(pdp_href, use_proxy=True)
        if res_pdp.status != 200:
            self.errors.raise_http_error(url=pdp_href)

        pdp_soup = self.get_soup(await res_pdp.text())
        desc_short, desc_long = self.scrape_descriptions(pdp_soup)
        variations, add_ons = self.scrape_variations_and_addons(pdp_soup)
        images = await self.scrape_images(pdp_soup)
        self.check_vars(variations, product_name, pdp_href)

        data = {
            'supplier': self.supplier,
            'brand': self.brand,
            'product': {
                'product_name': product_name,
                'description': desc_short,
                'description_long': desc_long,
                'is_on_sale': is_on_sale,
            },
            'prices': prices,
            'variations': variations,
            'add_ons': add_ons,
            'images': images,
        }
        return data


    async def run(self):

        page_counter = 1

        while True:
            await self.jitter(0.2, 0.5)
            print(f"\n{self.url}page/{page_counter}\n")
            res = await self.aio.get(f"{self.url}page/{page_counter}", use_proxy=True)
            if res.status != 200:
                dead_link_element = self.get_soup(await res.text()).select(self.selectors.dead_link)
                if dead_link_element:
                    break
                else:
                    self.errors.raise_http_error(url=self.url)
            page_counter += 1
            soup = self.get_soup(await res.text())
            product_cards = soup.select(self.selectors.product_cards)
            self.shuffle(product_cards)

            tasks = [self.scrape_product_card(product_card) for product_card in product_cards]
            for product_data in asyncio.as_completed(tasks):
                if not product_data:
                    continue
                yield await product_data



            # for product_card in product_cards:
            #     data = await self.scrape_product_card(product_card)
            #     if not data:
            #         continue

            #     yield data








                # print(data)
                # print("="*80)
                # print()
                # print(product_name)
                # print()
                # print(prices)
                # print()
                # if variations:
                #     print('VARS:')
                #     for variation in variations:
                #         print(variation['variation_type_name'])
                #         for value in variation['variation_values']:
                #             print(f"\t{value}")
                # else:
                #     print('VARS: none')
                # print()
                # if add_ons:
                #     print('ADD-ONS:')
                #     for add_on in add_ons:
                #         print('name: ' , add_on['name'])
                #         print('detail: ', add_on['detail'])
                #         print('price: ', add_on['price_modifier'])
                #         print('add_on_enum: ', add_on['add_on_enum'])
                # else:
                #     print('ADD ONS: none')
                # print()
                # print('===================================================')

