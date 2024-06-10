import asyncio
from typing import Any
from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.soup_base import SpiderTag, SpiderSoup
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
from webweaver.modules.project_modules.speed_fanatics.speed_enums import SubCategoryEnum, CategoryEnum




class EssexPartsSelectors:

    # index page
    side_menu = '.menu-side > ul'
    pagination = 'ul.pagination'
    product_category_links = '.menu-side > ul li.l3 > .grey-drop > a:first-of-type'
    product_cards = '.product-list-item'
    # product card
    product_img_main = '.product-image > img'
    product_name = '.title > h5'
    price = '.price'
    old_price = '.was'
    sale = '.prod-sale'
    pdp_link = 'a'
    # pdp page
    pdp_description = '.product-summary > p, .product-summary li'
    image_thumbnails = '.product-thumbs img'
    part_number = '.detail-section > p:first-of-type'
    brand = '.detail-section > p:nth-of-type(2)'
    product_options = '.product-options .option'
    # variation div
    option_name = 'label'
    option_values = 'option'


class CustomMappings:
    """Many of the product descriptions are quite useless. Brake pad descriptions, for example,
    provide no detail about the product. However brake fluid descriptions are quite useful.
    This mapping determines whether we are going to scrape a description for our product,
    or leave it null. This is based on the category
    """

    essex_category_name_to_subcategory_enum = {
        'big-brake-kits': SubCategoryEnum.BRAKE_KITS,
        'brake-discs': SubCategoryEnum.BRAKE_DISCS,
        'brake-hydraulics': SubCategoryEnum.BRAKE_FLUIDS,
        'master-cylinders': SubCategoryEnum.MASTER_CYLINDERS,
        'brake-bundles-pads-lines-fluid-discs': SubCategoryEnum.BRAKE_BUNDLES,
        'brake-pads': SubCategoryEnum.BRAKE_PADS,
        'brake-lines': SubCategoryEnum.BRAKE_LINES,
        'temperature-indication-and-protection-products': SubCategoryEnum.UNKNOWN,
        'tire-power127': SubCategoryEnum.TIRES_MISC,
        # 'formula-sae': ,
        # 'clearance-products': ,
    }

    # Some categories/descriptions aren't worth scraping.
    category_to_boolean = {
        'big-brake-kits': True,
        'brake-discs': True,
        'brake-hydraulics': True,
        'master-cylinders': True,
        'brake-bundles-pads-lines-fluid-discs': True,
        'brake-pads': False,
        'brake-lines': True,
        'temperature-indication-and-protection-products': True,
        'tire-power127': True,
        # 'formula-sae': True,
        # 'discounted-ferodo-pads': True,
    }




class EssexPartsSpider(PlaywrightSpider, SpeedSpiderMixin):

    selectors = EssexPartsSelectors
    category_links = [
        # 'aftermarket-products',
        'big-brake-kits',
        'brake-discs',
        'master-cylinders',
        'brake-bundles-pads-lines-fluid-discs',
        'brake-pads',
        'brake-hydraulics', # AKA brake fluids
        'brake-lines',
        'temperature-indication-and-protection-products',
        'tire-power127',
        # 'formula-sae',
        # 'discounted-ferodo-pads',
    ]
    # These categories have been excluded:
        # 'wheels'                  customer is instructed to contact essex parts directly to discuss wheels
        # 'suspension'              empty
        # 'promotion-and-apparel'   This is Essex-related clothing lol
        # 'discounted-ferodo-pads'  Confirm with buddy if we want to be doing these
        # 'brake-calipers'          everything here is $0 lol


    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        # self.url = 'https://www.essexparts.com/big-brake-kits?page=25'
        self.url = 'https://essexparts.com'


    # async def get_img_main(self, product_card:SpiderTag) -> bytes | None:
    #     """Scrape the binary data tha represents the product image
    #     NOTE there are more product images on the product pages! lots more lol
    #     """
    #     image_src_element = product_card.select_one(self.selectors.product_img_main)
    #     if image_src_element:
    #         image_src = image_src_element.get('src')
    #         if image_src:
    #             response = await self.aio.session.get(url=f"{self.url}{image_src}")
    #             if response.status == 200:
    #                 return await response.read()




    def check_bad_strings(self, s:str) -> str:
        """Remove any strings we dont want in the product description"""
        bad_strings = [
            "Please note that the first production run of this product is currently in process, so lead time will be longer than usual. Please call use for an expected date.",
        ]
        for bad_string in bad_strings:
            if bad_string in s:
                s.replace(bad_string, '')
        return s



    def get_product_name(self, product_card:SpiderTag) -> str:
        """Scrape the product name"""
        product_name = product_card.select_one(self.selectors.product_name)
        if not product_name:
            self.log('AttributeError: No product name found!!')
            raise AttributeError
        return product_name.text


    def get_price(self, product_card:SpiderTag) -> str:
        price = product_card.select_one(self.selectors.price)
        if not price:
            self.log('AttributeError: No price found!!')
            raise AttributeError
        return price.text


    def is_sale(self, product_card:SpiderTag) -> bool:
        sale_element = product_card.select_one(self.selectors.sale)
        return bool(sale_element)


    def get_pdp_link(self, product_card:SpiderTag) -> str:
        pdp_anchor_element = product_card.select_one(self.selectors.pdp_link)
        href = pdp_anchor_element.get('href')
        return f"{self.url}{href}"


    def split_option_value(self, option_value_string:str) -> tuple[str, str | None]:
        """add-ons and variations are annoyingly listed in the format:
        Ferodo DS2500 + $250.00
        Where the name and price are listed in the same string. These must
        be separated.
        """
        if option_value_string.find(' + $') != -1:
            return tuple([s.strip() for s in option_value_string.split(' + $')])
        return option_value_string, None



    def scrape_variations(self, label:SpiderTag, option_values:list[SpiderTag], is_required:bool) -> dict[str, str] | None:
        """Variation details to scrape:
            VariationType 
                -text
                -is_required
            ProductVariations
                -value
                -price_modifier

        *Remember label's text sometimes contains a '*' at the end which should be removed.
        """
        variation_values = []
        for option_value in option_values:
            value, price_modifier = self.split_option_value(option_value.text)
            variation_values.append({'value' : value, 'price_modifier' : price_modifier})
        return {
            'variation_type': {
                'variation_type_name': label.text,
                'is_required': is_required,
            },
            'variation_values': variation_values
        }


    async def scrape_image_urls(self, pdp_soup:SpiderSoup) -> list[dict[str, bytes]]:
        """Scrape the product image URLs by first converting this:
            /imagecache/productThumb/9668_372_enp_kit_6.png
        to this:
            https://www.essexparts.com/imagecache/productXLarge/9668_372_enp_kit_6.png
        """
        thumbnail_image_elements = pdp_soup.select(self.selectors.image_thumbnails)
        # print('thumbnail elements len: ', len(thumbnail_image_elements))

        image_urls = []
        for image_element in thumbnail_image_elements:
            thumbnail_url = image_element.get('src')
            path = thumbnail_url.replace('productThumb', 'productXLarge')
            # image_binary = await self.aio.scrape_image_url(url)
            image_urls.append({'image_url':f"{self.url}{path}"})

        return image_urls
    

    def remove_title_option(self, option_values:list[SpiderTag]) -> list[SpiderTag]:
        """Remove options from the list of options when they have values like:
            "- Select Add Brake Pads -"
        These are not real variation values, just titles/placeholders for the <select> elements
        """
        return [option for option in option_values if not option.text.strip().startswith("- ")]



    def scrape_options(self, pdp_soup:SpiderSoup) -> list[dict[str, str]]:
        """Required product variations contain '*' at the end.

        For example:
        Brake Pad Compound* -> required
        Disc Burnishing     -> not required
        
        *option_divs are divs with a class of '.option'
        *non-required variation is preferable to AddOns here because there
        are multiple possible values/choices for each option. I want to keep
        AddOns as essentially booleans/radio buttons.
        """
        variations = []

        option_divs = pdp_soup.select(self.selectors.product_options)
        if not option_divs:
            return
        for option_element in option_divs:
            label = option_element.select_one(self.selectors.option_name)
            option_values = option_element.select(self.selectors.option_values)
            option_values = self.remove_title_option(option_values)
            is_required = True if label.text.strip().endswith('*') else False
            vars_dict = self.scrape_variations(label, option_values, is_required)
            if vars_dict:
                    variations.append(vars_dict)

        return variations

    def confirm_product_name(self, product_name:str, product_code:str) -> str:
        """These guys have products with the same name! 
        Some products (brake-kits, possibly other categories too) have an 
        'Electroless Nickel Plated' finish option. These products will have
        a different product description, but identical product names. The 
        product code will have 'ENP' in it at the end so we can just check
        for that ENP substring and append it to the product name.
        """
        return f"{product_name} ENP" if 'ENP' in product_code.upper() else product_name


    def scrape_old_price(self, product_card:SpiderTag) -> str | None:
        """We do not get as good of a discount on sale items. So we do
        not want to scrape the sale price. We'll scrape the regular,
        non-sale price.
        """
        old_price = product_card.select_one(self.selectors.old_price)
        if old_price:
            return old_price.text


    async def scrape_detail_page(self, product_card:SpiderTag, link:str) -> dict[str, Any]:
        """Check the CustomMappings to see if we should be grabbing the
        description for this Essex Parts category.

        *This method makes an HTTP request
        """
        pdp_details = {}
        await self.jitter(0.25, 1)
        pdp_link = self.get_pdp_link(product_card)
        pdp_res = await self.aio.get(pdp_link, use_proxy=True)
        if pdp_res.status == 200:
            try:
                content = await pdp_res.text()
            except self.errors.ClientPayloadError:
                pdp_res = await self.aio.get(pdp_link, use_proxy=True)
                content = await pdp_res.text()

        soup_pdp = self.get_soup(content)
        # scrape product code:
        product_code:SpiderTag = soup_pdp.select_one(self.selectors.part_number)
        product_code.select_one_and_decompose('strong')
        pdp_details['product_code'] = product_code.text
        # scrape brand name:
        brand_element:SpiderTag = soup_pdp.select_one(self.selectors.brand)
        brand_element.select_one_and_decompose('strong')
        pdp_details['brand_name'] = brand_element.text
        # scrape variations:
        variations = self.scrape_options(soup_pdp)
        pdp_details['variations'] = variations
        # scrape images:
        image_urls = await self.scrape_image_urls(soup_pdp)
        pdp_details['image_urls'] = image_urls
        # scrape description if its a category that actually has descriptions:
        if CustomMappings.category_to_boolean.get(link):
            description_elements = soup_pdp.select(
                self.selectors.pdp_description)
            if len(description_elements) > 0:
                for description_element in description_elements:
                    for br in description_element.find_all('br'):
                        br.replace_with("\n\n")
                description = "\n".join([p.text for p in description_elements])
                pdp_details['description'] = self.check_bad_strings(description).strip()
        return pdp_details


    async def scrape_product(self, product_card:SpiderTag, link:str) -> dict:
        await self.jitter(0.5, 2)
        product_name = self.get_product_name(product_card)
        category, subcategory = self.get_categories(
            product_name=product_name,
            category_name=link,
            subcategory_mapping=CustomMappings.essex_category_name_to_subcategory_enum
        )
        price = self.scrape_old_price(product_card)
        if not price:
            price = self.get_price(product_card)
        is_sale = self.is_sale(product_card)
        pdp_details = await self.scrape_detail_page(product_card, link)

        product_name = self.confirm_product_name(
            product_name = product_name,
            product_code = pdp_details.get('product_code')
        )

        return {
            'supplier': self.supplier,
            'categories': {
                'category': category,
                'subcategory': subcategory,
            },
            'brand': {
                'brand_name': pdp_details.get('brand_name')
            },
            'product': {
                'product_name': product_name,
                'product_code': pdp_details.get('product_code'),
                'description': pdp_details.get('description'),
                'is_sale': is_sale
            },
            'price': {
                'msrp': price,
            },
            'image_urls': pdp_details.get('image_urls'),
            'variations': pdp_details.get('variations'),
        }


    async def _test_category_link(self, category_link:str) -> int:

        res = await self.aio.get(f"{self.url}/{category_link}", use_proxy=True)
        return res.status


    async def run(self):

        # Iterate through the Essex Parts categories:
        for link in self.category_links:

            counter = 1

            # Iterate through pagination for this category:
            while True:
                if counter == 1:
                    res = await self.aio.get(f"{self.url}/{link}", use_proxy=True)
                    # res = await self.aio.get('https://www.essexparts.com/big-brake-kits?page=4', use_proxy=True)
                else:
                    res = await self.aio.get(f"{self.url}/{link}?page={counter}", use_proxy=True)
                if res.status == 200:
                    counter += 1
                    soup = self.get_soup(await res.text())
                    product_cards = soup.select(self.selectors.product_cards)
                    if len(product_cards) == 0:
                        break

                    # Scrape the product cards on this page:
                    self.shuffle(product_cards)
                    tasks = [self.scrape_product(product_card, link) for product_card in product_cards]
                    for product_data in asyncio.as_completed(tasks):
                        awaited_data = await product_data
                        print('product: ', awaited_data['product']['product_name'])
                        print('price: ', awaited_data['price']['msrp'])
                        print('img url: ', awaited_data['image_urls'][0]['image_url'])
                        print()
                        yield awaited_data

                    pagination = soup.select_one(self.selectors.pagination)
                    if not pagination:
                        print('no pagination!')
                        break
                else:
                    print('blehhhhhh')
                    break

        yield {}


