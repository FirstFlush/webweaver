from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.soup_base import SpiderTag, SpiderSoup
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    SupplierEnum,
    CategoryEnum, 
    WheelAttributeEnum, 
    TireAttributeEnum
)

class VerusEngineeringSelectors:

    product_cards = 'td.oe_product'
    next_button = 'ul.pagination > li:last-of-type'

    # in product cards:
    product_name = 'h6'
    price = '.oe_currency_value'
    pdp_link = 'h6 a'  #href

    # pdp:
    descriptions = '#product_full_description .card-body'
    images = '#o-carousel-product .o_carousel_product_outer img'


class VerusEngineeringSpider(PlaywrightSpider, SpeedSpiderMixin):

    selectors = VerusEngineeringSelectors


    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = "https://www.verus-engineering.com/shop"
        self.brand = {'brand_name' : 'Verus Engineering'}


    def is_final_page(self, soup:SpiderSoup) -> bool:
        """Pagination does not throw error or non-200 response code when
        we navigate to product index pages that don't exist.

        *Currently, /page/24 is the last page of all products.
        This function ensures we can break out of the while-loop if the
        'next button' (<li> element) contains the class 'disabled'.
        """
        next_button = soup.select_one(self.selectors.next_button)
        if 'disabled' in next_button.get('class',[]):
            return True
        return False


    def scrape_description(self, pdp_soup:SpiderSoup) -> str | None:
        """PDP page has two boxes for description. 
        
        Box #1 has a paragraph-form overview of the product.
        Box #2 has a <ul> with <li> elements declaring what exactly is included with the product

        I handle each box differently since their logic is a bit different.
        """
        description_elements = pdp_soup.select(self.selectors.descriptions)
        if len(description_elements) == 0:
            return

        description_elements = description_elements[:-1]

        description_overview = []
        for content in description_elements[0].contents:
            content_text = content.text.strip()
            if content_text:
                description_overview.append(content_text)

        try:
            whats_included = []
            li_elements = description_elements[1].select('li')
            for li_element in li_elements:
                # print("li element: ",li_element)
                li_text = li_element.text.strip()
                if li_text:
                    whats_included.append(li_text)

            description_whats_included = '\n'.join(whats_included)
            description_whats_included = "WHAT IS INCLUDED\n\n" + description_whats_included
            description_overview_text = "\n\n".join(description_overview)
            return description_overview_text + "\n\n\n" + description_whats_included
        except IndexError:
            #TODO this is hacky and temporary:
            description_overview_text = "\n\n".join(description_overview)
            return description_overview_text


    # def get_description_li_text(self) -> str:


    async def scrape_images(self, pdp_soup:SpiderSoup) -> list[dict[str, bytes]]:
        """Scrape images from pdp page. This part seems easy and smooth."""
        image_elements = pdp_soup.select(self.selectors.images)
        images = []
        for image_element in image_elements:
            await self.jitter(0.2, 0.5)
            image_bytes = await self.aio.scrape_image(image_element)
            if image_bytes:
                images.append({'image' : image_bytes})
        return images
    

    async def scrape_product_card(self, product_card:SpiderTag) -> dict:
        product_name = product_card.select_one(self.selectors.product_name).text
        price = product_card.select_one(self.selectors.price).text
        pdp_href = product_card.select_one(self.selectors.pdp_link)['href']
        pdp_url = f"https://{self.domain}/{pdp_href}"
        pdp_res = await self.aio.get(pdp_url)
        if pdp_res.status != 200:
            self.errors.raise_http_error()
        pdp_soup = self.get_soup(await pdp_res.text())
        description = self.scrape_description(pdp_soup)
        images = await self.scrape_images(pdp_soup)

        data = {
            'supplier': self.supplier,
            'brand': self.brand,
            'product' : {
                'product_name': product_name,
                'description': description
            },
            'price' : {
                'msrp': price,
            },
            'images' : images 
        } 
        return data



    async def run(self):

        # page_counter = 0
        page_counter = 14

        while True:
            page_counter += 1
            await self.jitter(0.5, 1)
            url_to_scrape = f"{self.url}/page/{page_counter}"
            print()
            print('URL TO SCRAPE: ', url_to_scrape)
            print()
            res = await self.aio.get(url_to_scrape, use_proxy=True)
            if res.status != 200:
                self.errors.raise_http_error()

            soup = self.get_soup(await res.text())

            # Check to make sure we are not on the final page
            if self.is_final_page(soup):
                break

            product_cards = soup.select(self.selectors.product_cards)    
            self.shuffle(product_cards)    
            for product_card in product_cards:
                data = await self.scrape_product_card(product_card)

                yield data