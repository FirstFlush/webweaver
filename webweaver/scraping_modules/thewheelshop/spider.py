import asyncio
from typing import TYPE_CHECKING

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider 
from webweaver.webscraping.spiders.soup_base import SpiderTag, SpiderSoup
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    TheWheelShopCollectionEnum, 
    CategoryEnum, 
    WheelAttributeEnum, 
    TireAttributeEnum
)

if TYPE_CHECKING:
    from webweaver.modules.project_modules.speed_fanatics.product_attributes.attribute_handler import AttributeHandler


class TheWheelShopSelectors:

    # Nav menu:
    collection_groups = '.grid__item.medium-up--one-fifth' 
    collection_group_name = '.site-nav__dropdown-link--top-level'
    collection_links_in_group = '.site-nav__dropdown-link:not(.site-nav__dropdown-link--top-level)'

    # Footer:
    #NOTE this currency feature seems to be removed from the site. 
    currency_canada = 'button.faux-select .currency-flag--ca' # check if it exists. If not, you are looking at American prices for everything.

    # Collection page:
    product_cards = '.grid__item.grid-product'

    # on product card:
    product_name = '.grid-product__title'
    brand = '.grid-product__vendor'
    price = '.grid-product__price'
    price_old = '.grid-product__price--original'
    sold_out = '.grid-product__tag--sold-out'
    is_sale = '.grid-product__tag--sale'
    pdp_link = '.grid-product__link'
    image_main = 'img.grid__image-contain'

    # pdp:
    price_pdp = '.product-block--price .product__price:not(.product__price--compare)'
    price_pdp_old = '.product-block--price .product__price--compare'
    attributes = '.product-single__meta .variant-wrapper'
    attribute_type = 'fieldset'  # from attributes, get name attribute
    attribute_value = '.variant-input'  # from attributes, get data-value attribute
    description = '.product-single__meta .rte:not(.collapsible-content__inner)'
    add_ons = '.product-single__meta .gpo-choicelist'
    image_thumbnails = '.product__thumbs--scroller img'
    image_main_pdp = '.product-image-main img'
    product_code = '.product-single__sku'


# class WheelShopTesting:

#     def __init__(self, spider:"TheWheelShopSpider"):
#         self.spider = spider


#     def skip_collections(self, collections, substrings*) -> list:

#         s = ' '.join(substrings)
#         if '-wheels' in s or 'tires' in s:
        
#         continue



class WheelShopMappings:

    collections_to_category_enum = {
        # wheels
        '4 lugs' : CategoryEnum.WHEELS,
        '5 lugs' : CategoryEnum.WHEELS,
        '6 lugs' : CategoryEnum.WHEELS,
        '7 lugs' : CategoryEnum.WHEELS,
        '8 lugs' : CategoryEnum.WHEELS,
        # tires
        'summer tires' : CategoryEnum.TIRES,
        'winter tires' : CategoryEnum.TIRES,
        'all terrain tires' : CategoryEnum.TIRES,
        'mud terrain tires' : CategoryEnum.TIRES,
        # wheel accessories
        'adapters | hub rings | spacers' : CategoryEnum.WHEEL_ACCESSORIES,
        'center caps | emblems | inserts' : CategoryEnum.WHEEL_ACCESSORIES,
        'bolts | nuts' : CategoryEnum.WHEEL_ACCESSORIES,
        # tire accessories
        'tpms | valves | studs' : CategoryEnum.TIRE_ACCESSORIES,
        # exhaust
        'exhaust' : CategoryEnum.EXHAUST,
        # intake
        'intake' : CategoryEnum.INTAKE,
        # suspension
        'suspension' : CategoryEnum.SUSPENSION,
    }


class TheWheelShopSpider(PlaywrightSpider, SpeedSpiderMixin):

    selectors = TheWheelShopSelectors
    custom_mapping = WheelShopMappings


    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        # self.testing = WheelShopTesting(self)
        self.url = 'https://thewheelshop.ca/'
        self.fuzzy_handler_wheel = self.project_handler.fuzzy_handler.get_handler_from_enum(WheelAttributeEnum, 'product')
        self.fuzzy_handler_tires = self.project_handler.fuzzy_handler.get_handler_from_enum(TireAttributeEnum, 'product')


    def build_collection_link(self, collection_name:str) -> str:
        """Collections is a term used on the site. It is essentially 
        a sub-subcategory. Example:

        category:   subcategory:    collection:
        wheels      5 lugs          5x100
        ''          ''              5x105
        ''          ''              5x108

        The returned URL includes a GET parameter to only include 
        products that are in-stock.
        """
        if not collection_name:
            raise TypeError(f"{self.spider_asset.spider_name} collection_name is None")

        return f"https://{self.spider_asset.domain}{collection_name}?filter.v.availability=1"



    def attributes_from_description(self, pdp_soup:SpiderSoup) -> list[str]:
        description = pdp_soup.select_one(self.selectors.description)
        description_lines = []
        for content in description.contents:
            if content:
                if content.name != 'br':
                    try:
                        description_lines.append(content.strip())
                    except TypeError as e:
                        self.log(TypeError(e))
                        pass
        return description_lines


    def split_attr_line(self, attr_line:str) -> tuple[str, str]:
        """Returns 'Centerbore: 125.1' as ('Centerbore', '125.1')"""
        return tuple(attr_line.split(':',1))


    def scrape_wheel_attributes_from_attrs_list(self, attr_handler:"AttributeHandler", attrs_list:list[str]):
        """Wheel attributes are often listed in the description, as key-value pairs"""
        for attr_line in attrs_list:
            if ':' not in attr_line:
                continue
            attr_key, attr_value = self.split_attr_line(attr_line)
            attr_key_lower = attr_key.lower()
            if 'size' in attr_key_lower and 'lip' not in attr_key_lower:
                diameter, width = self.split_wheel_size(attr_value)
                attr_handler.wheel_attributes.diameter = diameter
                attr_handler.wheel_attributes.width = width
            if 'bolt pattern' in attr_key_lower:
                attr_handler.wheel_attributes.bolt_pattern = attr_value
            if 'offset' in attr_key_lower:
                attr_handler.wheel_attributes.offset = attr_value
            if 'centerbore' in attr_key_lower:
                attr_handler.wheel_attributes.centerbore = attr_value
            if 'load rating (lbs)' in attr_key_lower:
                try:
                    load_rating = self.lbs_to_kg(attr_value)
                except ValueError:
                    load_rating = attr_value
                attr_handler.wheel_attributes.load_rating = load_rating
            elif 'load rating' in attr_key_lower:
                attr_handler.wheel_attributes.load_rating = attr_value
            if 'weight' in attr_key_lower:
                attr_handler.wheel_attributes.weight = attr_value
            if 'backspacing' in attr_key_lower:
                attr_handler.wheel_attributes.backspacing = attr_value
            if 'color' in attr_key_lower:
                attr_handler.wheel_attributes.finish = attr_value


    def scrape_wheel_attributes(
            self, 
            attr_handler:"AttributeHandler", 
            product_name:str,
            pdp_soup:SpiderSoup
    ):
        attrs_list = self.attributes_from_description(pdp_soup)
        self.scrape_wheel_attributes_from_attrs_list(
            attr_handler=attr_handler, 
            attrs_list=attrs_list
        )

    def scrape_tire_attributes(
            self, 
            attr_handler:"AttributeHandler", 
            product_name:str,
            pdp_soup:SpiderSoup
    ):
        attr_handler.scrape_tire_data_from_string(product_name)



    def scrape_product_attributes(
            self, 
            category_enum:CategoryEnum,
            product_name:str,
            pdp_soup:SpiderSoup
        ) -> "AttributeHandler":
        """Scrape wheel or tire attributes from the page and return them as a dict."""
        attribute_handler = self.attribute_handler(category_enum)

        if attribute_handler.category_enum == CategoryEnum.WHEELS:
            self.scrape_wheel_attributes(
                attr_handler = attribute_handler,
                product_name = product_name,
                pdp_soup = pdp_soup
            )

        elif attribute_handler.category_enum == CategoryEnum.TIRES:
            self.scrape_tire_attributes(
                attr_handler = attribute_handler,
                product_name = product_name,
                pdp_soup = pdp_soup
            )

        return attribute_handler


    def scrape_price(self, price_div:SpiderTag) -> list[dict[str, str]]:
        """Returns a tuple of price and the old price (crossed out price on page)"""
        price_old = price_div.select_one_and_extract(self.selectors.price_old)
        price_old = price_old.text.strip() if price_old else None
        price_div.select_and_decompose('span')
        price = price_div.text.strip()
        return [
            {
                'msrp': price
            },
            {
                'msrp': price_old,
                'is_old': True
            }
        ]


    def get_pdp_link(self, anchor_tag:SpiderTag) -> str:
        href = anchor_tag.get('href')
        return f"https://{self.spider_asset.domain}{href}"


    def scrape_add_on(self, add_on_element:SpiderTag) -> dict:
        details = add_on_element.select('span')
        return {
            'add_on_detail': details[0].text,
            'add_on_price': details[1].text,
        }



    def scrape_description(self, pdp_soup:SpiderSoup) -> str | None:
        """Scrape the product description. Many products will not have a description
        For certain products, like tires/wheel-related products, description contains
        important details like bolt_pattern and load_rating.
        """
        description = pdp_soup.select_one(self.selectors.description)
        if description:
            for br in description.select('br'):
                br.replace_with('\n')
            return description.text if description.text != '\n' else None


    def scrape_product_code(self, pdp_soup:SpiderSoup) -> str:
        try:
            return pdp_soup.select_one(self.selectors.product_code).text.strip()
        except AttributeError as e:
            msg = f"Product code: '{pdp_soup.select_one(self.selectors.product_code)}'"
            raise AttributeError(msg) from e


    def scrape_image_urls(self, pdp_soup:SpiderSoup) -> list[dict[str, str]]:
        image_urls = []
        image_elements = pdp_soup.select(self.selectors.image_thumbnails)
        image_elements.extend(pdp_soup.select(self.selectors.image_main_pdp))
        for image_element in image_elements:
            image_urls.append({'image_url' : self.clean_url(image_element.get('src'))})
        return image_urls


    async def scrape_images(self, pdp_soup:SpiderSoup) -> list[dict[str, bytes]]:
        image_elements = pdp_soup.select(self.selectors.image_thumbnails)
        if not image_elements:
            image_elements.append(pdp_soup.select_one(self.selectors.image_main_pdp))
        images = []
        for image_element in image_elements:
            image_bytes = await self.aio.scrape_image(image_element)
            if image_bytes:
                images.append({'image' : image_bytes})
        return images


    def scrape_brand_name(self, product_card:SpiderTag) -> str|None:
        brand = product_card.select_one(self.selectors.brand)
        return brand.text if brand else None


    async def scrape_product_card(self, product_card:SpiderTag, collection_enum:TheWheelShopCollectionEnum):

        if product_card.select_one(self.selectors.sold_out):
            return 

        product_name_element = product_card.select_one(self.selectors.product_name)
        pdp_link_element = product_card.select_one(self.selectors.pdp_link)

        product_name = product_name_element.text
        is_sale = bool(product_card.select_one(self.selectors.is_sale))
        brand_name = self.scrape_brand_name(product_card)

        price_div = product_card.select_one(self.selectors.price)
        prices = self.scrape_price(price_div=price_div)


        pdp_link = self.get_pdp_link(pdp_link_element)
        
        await self.jitter(0.2, 0.5)
        pdp_res = await self.aio.get(pdp_link)
        if pdp_res.status != 200:
            self.errors.raise_http_error()
            # self.log(f"PDP ERROR: received status code{pdp_res.status} when requesting {pdp_link}")

        pdp_soup = self.get_soup(await pdp_res.text())

        description = self.scrape_description(pdp_soup)
        product_code = self.scrape_product_code(pdp_soup)
        category, subcategory = self.get_categories(
            product_name = product_name,
            category_name = collection_enum.value.lower(),
            category_mapping = self.custom_mapping.collections_to_category_enum
        )

        # images = await self.scrape_images(pdp_soup)
        image_urls = self.scrape_image_urls(pdp_soup)

        category_enum = self.custom_mapping.collections_to_category_enum.get(collection_enum.value.lower())
        match category_enum:
            case CategoryEnum.WHEELS | CategoryEnum.TIRES:
                attribute_handler = self.scrape_product_attributes(
                    category_enum=category_enum,
                    product_name=product_name,
                    pdp_soup=pdp_soup,
                )
                if attribute_handler.final_check():
                    wheel_attributes = attribute_handler.wheel_dict
                    tire_attributes = attribute_handler.tire_dict
                else:
                    self.log(f"[ATTR ERROR] Final check failed: {product_name}")
                    return
            case _:
                wheel_attributes = None
                tire_attributes = None

        # print('product: \t', product_name)
        # print('code: \t\t', product_code)
        # print('cat: \t\t', category.category_enum)
        # print('subcat: \t', subcategory.subcategory_enum)
        # print()

        data = {
            'supplier': self.supplier,
            'categories': {
                'category': category,
                'subcategory': subcategory,
            },
            'brand': {
                'brand_name': brand_name,
            },
            'product': {
                'product_name': product_name,
                'product_code': product_code,
                'is_sale': is_sale,
                'description': description,
            },
            'prices': [price for price in prices if price['msrp']],
            'wheel_attributes': wheel_attributes, 
            'tire_attributes': tire_attributes,

            'image_urls': image_urls
        }
        print(data['product']['product_name'])
        print(data['wheel_attributes'])
        print()
        return data

    async def run(self):

        res = await self.aio.get(self.url)
        if res.status != 200:
            self.errors.raise_http_error()

        soup = self.get_soup(await res.text())
        
        collection_groups = soup.select(self.selectors.collection_groups)
        
        all_collections:dict[TheWheelShopCollectionEnum, list[str]] = {}

        # Build mapping of collection enum to collections
        for collection_group in collection_groups:
            collection_group_name_element = collection_group.select_one(self.selectors.collection_group_name)
            collection_group_name = collection_group_name_element.text.strip()
            for collection_enum in TheWheelShopCollectionEnum:
                if collection_enum.value == collection_group_name:
                    collection_enum = collection_enum
                    break
            collections = [self.build_collection_link(anchor_element.get('href'))
                           for anchor_element in
                           collection_group.select(self.selectors.collection_links_in_group)]
            all_collections[collection_enum] = collections


        for collection_enum, collection_links in all_collections.items():
            for collection_link in collection_links:


                #NOTE testing
                if '-wheels' in collection_link.lower():
                    print(collection_link, ' skipping....')
                    continue

                await self.jitter(0.2, 0.5)
                
                res_collection = await self.aio.get(collection_link)
                if res_collection.status != 200:
                    self.errors.raise_http_error()

                soup = self.get_soup(await res_collection.text())
                product_cards = soup.select(self.selectors.product_cards)
                self.shuffle(product_cards)

                # scrape product cards
                tasks = [self.scrape_product_card(
                    product_card = product_card, 
                    collection_enum = collection_enum
                    ) for product_card in product_cards
                ]

                for product_data in asyncio.as_completed(tasks):
                    awaited_data = await product_data
                    
                    if not awaited_data:
                        continue

                    # for key, value in awaited_data.items():
                    #     print(key, " : ", value)
                    #     print()

                    yield awaited_data






                # force CAD currency:
                # while True:
                #     res_collection = await self.aio.get(collection_link)
                #     if res_collection.status != 200:
                #         self.errors.raise_http_error()

                #     soup = self.get_soup(await res_collection.text())
                #     canada_currency = soup.select_one(self.selectors.currency_canada)
                #     print('Currency check: ', canada_currency)             
                #     if canada_currency:
                #         break
                #     else:
                #         await self.jitter(0.2, 0.5)
                #         continue




