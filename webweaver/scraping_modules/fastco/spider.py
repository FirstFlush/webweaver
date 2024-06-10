from playwright.async_api import ElementHandle, Page, TimeoutError as PlaywrightTimeoutError
import os
import validators

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.spider_page import SpiderPage
from webweaver.webscraping.spiders.soup_base import SpiderSoup, SpiderTag
from webweaver.modules.project_modules.speed_fanatics.speed_spider import SpeedSpiderMixin
from webweaver.modules.project_modules.speed_fanatics.speed_enums import (
    TireAttributeEnum, 
    WheelAttributeEnum,
    CategoryEnum,
    SubCategoryEnum,
)


class FastcoSelectors:
    
    # Login
    modal_close = '#newsletterModal .close'
    username_input = '#p_lt_ctl05_pageplaceholder_p_lt_ctl01_WebPartZone2_WebPartZone2_zone_WebPartZone_WebPartZone_zone_LogonForm_Login1_UserName'
    password_input = '#p_lt_ctl05_pageplaceholder_p_lt_ctl01_WebPartZone2_WebPartZone2_zone_WebPartZone_WebPartZone_zone_LogonForm_Login1_Password'
    btn_sign_in = '#p_lt_ctl05_pageplaceholder_p_lt_ctl01_WebPartZone2_WebPartZone2_zone_WebPartZone_WebPartZone_zone_LogonForm_Login1_LoginButton'

    # Brand filtering
    tire_brand_select = '#tirebrand'  # <select>
    tire_brands = '#tirebrand > option'
    wheel_brand_select = '#wheelbrand'
    wheel_brands = '#wheelbrand > option'
    btn_search = '#search'
    results_select = '.displaySelect'  # <select> controlling # of results (products) per page (from 12 to 'all')
    result_count = '.itemCount'  # total number of scrape-able products on this page

    # Product table
    product_table = '#sortTable'
    product_rows = '.table-row'  # take from product_table

    # Product row (products)
    image = 'a img'  # get the src
    tire_name = 'td:nth-of-type(5) app-product-details-modal'
    tire_product_code = 'td:nth-of-type(5) .sku-tooltip'
    tire_description = 'td:nth-of-type(6)'
    tire_type = 'td:nth-of-type(7)'
    tire_utqg = 'td:nth-of-type(8)'
    tire_od = 'td:nth-of-type(9)'
    tire_studdable = 'td:nth-of-type(10)'
    tire_msrp = 'td:nth-of-type(13) .withoutPadding'

    wheel_name = 'td:nth-of-type(3) app-product-details-modal'
    wheel_product_code = 'td:nth-of-type(3) .sku-tooltip'
    wheel_size = 'td:nth-of-type(5)'
    wheel_bolt_pattern = 'td:nth-of-type(6)'
    wheel_offset = 'td:nth-of-type(7)'
    wheel_seat = 'td:nth-of-type(8)'
    wheel_centerbore = 'td:nth-of-type(9)'
    wheel_weight = 'td:nth-of-type(10)' # lbs
    wheel_finish = 'td:nth-of-type(11) span' # take data-original-title attribute
    wheel_msrp = 'td:nth-of-type(14) .withoutPadding'

    inventory = 'td:nth-of-type(11)'
    calgary_qty = '#calgary-Qty > span'
    montreal_qty = '#montreal-Qty > span'
    on_order_eta = 'td:nth-of-type(12)'
    
    #pagination
    next_page = 'ul.ngx-pagination > li.current + li'


class FastcoSpider(PlaywrightSpider, SpeedSpiderMixin):
    """This spider should always scrape slowly since we have to login just to view the products.
    Product index will only show max 1000 results if you try to search tires or wheels by "all".
    You have to search by brand, and if the product count for any brand exceeds 1000 then that
    brand must be filtered by 'tire type': summer, winter, all-weather, all-season.
    """
    selectors = FastcoSelectors

    USERNAME = os.getenv('FASTCO_USER')
    PASSWORD = os.getenv('FASTCO_PASS')

    url_tires_by_brand = 'https://fastco.ca/fastfinder/shop/search-by-brand/tires'
    url_wheels_by_brand = 'https://fastco.ca/fastfinder/shop/search-by-brand/wheels'
    slow_loading_brands = {
        'braelin',
        'fast wheels',
    }
    broken_brands = {
        'fast ev',
    }


    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = 'https://fastco.ca/Fastco-Canada/Login'


    async def set_all_results(self, spider_page:SpiderPage, is_slow:bool=False, product_count:int=100000) -> bool:
        """Changes the # of products per page from 24 to 'all',
        defined on Fastco as 100000 because those are totally the same thing.

        Returns a bool... maybe bad design.. But returns the bool to let the
        calling function know the 'all' value has been set and this function
        doesn't need to be called again.
        """
        all_value = str(product_count)
        results_select = await spider_page.page.query_selector(self.selectors.results_select)
        if results_select:
            await spider_page.page.select_option(
                selector=self.selectors.results_select,
                element=results_select,
                value=all_value
            )
            if is_slow:
                timeout = 120000
            else:
                timeout = 50000
            await spider_page.page.wait_for_selector(self.selectors.product_table, timeout=timeout)
            return True
        return False


    async def iter_brand(
            self, 
            brand_option:ElementHandle, 
            spider_page:SpiderPage,
            product_category:CategoryEnum
    ) -> bool:
        """Iterate through the brands. This involves selecting the brand from a <select> element
        and then submitting an ajax request, receiving the response.

        The next step after this is to wait for the stupidly-slow product table to load.
        """
        option_value = await brand_option.get_attribute('value')
        brand_name = await brand_option.text_content()
        brand_name_lower = brand_name.lower().strip()

        print()
        print(brand_name_lower, "scrape ittt")
        print()

        if brand_name_lower == 'brand' or option_value == 'null':
            return False
        elif brand_name_lower in self.broken_brands:
            print()
            print('BROKEN BRAND: ', brand_name_lower)
            print()
            return False


        if product_category == CategoryEnum.TIRES:
            await spider_page.page.select_option(self.selectors.tire_brand_select, option_value)
        elif product_category == CategoryEnum.WHEELS:
            await spider_page.page.select_option(self.selectors.wheel_brand_select, option_value)
        else:
            raise ValueError('product_type passed to iter_brand() is not a valid CategoryEnum!')
        search_btn = await spider_page.page.query_selector(self.selectors.btn_search)
        await search_btn.click()
        if brand_name_lower in self.slow_loading_brands:
            await self.jitter(30, 45)
        else:
            await self.jitter(8, 15)
        return True


    async def result_count(self, spider_page:SpiderPage) -> int:
        result_count = await spider_page.page.query_selector(self.selectors.result_count)
        result_count_text = await result_count.text_content()
        if result_count_text == ' No Results Found':
            return 0
        try:
            return int(''.join([char for char in result_count_text.split('of')[1] if char.isdigit()]))
        except Exception as e:
            raise e



    async def scrape_tires_by_brand(self, spider_page:SpiderPage):

        await spider_page.goto_or_none(self.url_tires_by_brand)
        await spider_page.page.wait_for_load_state(state='load', timeout=30000)
        await spider_page.page.wait_for_selector(self.selectors.tire_brand_select)
        tire_brands = await spider_page.page.query_selector_all(self.selectors.tire_brands)

        set_all = False
        for tire_brand in tire_brands:
            brand_name = await tire_brand.text_content()
            if not await self.iter_brand(tire_brand, spider_page, CategoryEnum.TIRES):
                continue

            if not set_all:
                set_all = await self.set_all_results(spider_page)
            try:
                await spider_page.page.wait_for_selector('tbody', timeout=100000)
            except PlaywrightTimeoutError as e:
                print(f'no tires found for brand `{brand_name}`, skipping..')
                continue


            result_count = await self.result_count(spider_page)
            if result_count == 1000:
                #TODO logic for this?
                print(f'{brand_name.strip()} exceeds 1000 results')
            
            product_table = await spider_page.page.query_selector(self.selectors.product_table)
            if product_table:
                soup = self.get_soup(await product_table.inner_html())

                product_rows = soup.select(self.selectors.product_rows)
                for product_row in product_rows:
                    tire_data = self.scrape_tire(product_row)
                    if tire_data:
                        tire_data['brand'] = {'brand_name': brand_name.strip()}
                        tire_data['supplier'] = self.supplier

                    yield tire_data
                print()
                print(len(product_rows))
                print('----------------------')


    def get_inventory_qty(self, tire_row:SpiderTag) -> int:
        """Get the inventory quantity as an int by adding up inventories between
        calgary and montreal.

        This function is mainly to check if the total inventory level is 0
        Or perhaps below 4 I should check. Since most people will buy in 4s.
        """
        calgary_qty = tire_row.select_one_text(self.selectors.calgary_qty)
        montreal_qty = tire_row.select_one_text(self.selectors.montreal_qty)
        if calgary_qty and montreal_qty:
            qty = 0
            for qty_value in [calgary_qty, montreal_qty]:
                qty += int(''.join([char for char in qty_value if char.isdigit()]))
            return qty
        return 0


    def get_tire_code(self, description_element:SpiderTag) -> str:
        """Returns the tire size/code. Examples:

            245/60R18 105T
            305/30ZR19 102W
            195/60R14 86H
        """
        return description_element.get_text(strip=True, separator='|').split('|')[0]


    def scrape_overall_diameter(self, od_element:SpiderTag) -> str|None:
        text_parts = od_element.get_text(strip=True, separator='|').split('|')
        return text_parts[0]


    def scrape_utqg(self, utqg_element:SpiderTag) -> str|None:
        """Careful to ensure '' returns as None"""

        # print('utqg element: ', utqg_element)

        utqg = utqg_element.get_text(separator=' ').strip()
        # print('utqg: ', utqg)
        return utqg if utqg else None


    def scrape_studdable(self, studdable_element:SpiderTag) -> bool:
        match studdable_element.text.lower().strip():
            case 'yes':
                return True
            case 'no':
                return False
            case _:
                raise self.errors.WebScrapingError(
                    f"Can't determine bool from studdable value: {studdable_element.text.lower().strip()}"
                )

    def scrape_cost(self, price_element:SpiderTag) -> str:
        """cost_string example:     

        Sometimes: "Net Price: $156.80" 
        Sometimes: "Net Price: $254.79<br/>Minimum Advertised Price: $342.99"
        
        A pox on whoever wrote Fastco's HTML.
        """
        cost_string = price_element.get('data-original-title')
        try:
            cost =  cost_string.split(':')[1].strip()
        except (AttributeError, IndexError) as e:
            raise self.errors.WebScrapingError from e
        if '<br' in cost:
            cost = cost.split('<br')[0]
        return cost



    def scrape_image_url(self, img_element:SpiderTag) -> str|None:
        """The image URL for this img_element will be a thumbnail. However
        there is a larger image at an insecure endpoint that can be scraped later.
        The URL has to be adjusted slightly.

        Example:
        https://fastcob2bstore.blob.core.windows.net/fastco-media/fastco/media/b2bThumb/NANKANG-AS-2PLUS-X.JPG
        must become:
        https://fastcob2bstore.blob.core.windows.net/fastco-media/fastco/media/b2b/NANKANG-AS-2PLUS.JPG
        """
        src = img_element.get('src') if img_element else None
        if src:
            return (src[:-6] + src[-4:]).replace('Thumb','')


    def scrape_product_name(self, product_name_element:SpiderTag, tire_code:str) -> str:
        """Fastco products sometimes have identical names.
        The tire code is appended to the product name to keep
        product names unique & descriptive.
        """
        if not product_name_element:
            raise self.errors.WebScrapingError(f"No product name found for tire code '{tire_code}'")
        return f"{product_name_element.text.strip()} {tire_code.strip()}"


    def scrape_tire(self, tire_row:SpiderTag) -> dict:

        img_element = tire_row.select_one(self.selectors.image)
        tire_name_element = tire_row.select_one(self.selectors.tire_name)
        description_element = tire_row.select_one(self.selectors.tire_description)
        tire_type_element = tire_row.select_one(self.selectors.tire_type)
        utqg_element = tire_row.select_one(self.selectors.tire_utqg)
        overall_diameter_element = tire_row.select_one(self.selectors.tire_od)
        studdable_element = tire_row.select_one(self.selectors.tire_studdable)
        price_element = tire_row.select_one(self.selectors.tire_msrp)
        product_code_element = tire_row.select_one(self.selectors.tire_product_code)
        inventory_qty = self.get_inventory_qty(tire_row)

        subcategory_enum = self.speed_mapping.text_to_subcategory_enum.get(
            self.fuzzing.preprocess(tire_type_element.text)
        )

        tire_code = self.get_tire_code(description_element)
        try:
            tire_attributes = self.tire_attributes_from_tire_code(tire_code)
        except self.errors.WebScrapingError as e:
            self.log(msg=e)
            return
        
        tire_attributes[TireAttributeEnum.UTQG] = self.scrape_utqg(utqg_element)
        tire_attributes[TireAttributeEnum.STUDDABLE] = self.scrape_studdable(studdable_element)
        tire_attributes[TireAttributeEnum.OVERALL_DIAMETER] = self.scrape_overall_diameter(overall_diameter_element)

        tire_attributes_dict = {key.value: value for key, value in tire_attributes.items()}

        data = {
            'categories': {
                'category': self.get_category_from_enum(CategoryEnum.TIRES),
                'subcategory' : self.get_subcategory_from_enum(subcategory_enum)
            },
            'product': {
                'product_name': self.scrape_product_name(tire_name_element, tire_code),
                'description': description_element.get_text(separator='\n', strip=True),
                'product_code': product_code_element.text,
            },
            'price': {
                'msrp': price_element.text,
            },
            'cost': {
                'cost': self.scrape_cost(price_element),
            },
            'tire_attributes' : tire_attributes_dict,
            'wheel_attributes' : None,
            'image_url': {
                'image_url': self.scrape_image_url(img_element)
            }
        }


        return data


    def scrape_prices(self, msrp_element:SpiderTag) -> tuple[str, str]:
        """Scrape both our price and the msrp price from the msrp element."""
        msrp = msrp_element.text
        our_price = msrp_element.get('data-original-title')
        our_price = our_price.split(':')[1].strip()
        return (msrp, our_price)



    async def scrape_wheels_by_brand(self, spider_page:SpiderPage):
        
        await spider_page.goto_or_none(self.url_wheels_by_brand)
        await spider_page.page.wait_for_load_state(state='load', timeout=50000)
        await spider_page.page.wait_for_selector(self.selectors.wheel_brand_select)
        wheel_brands = await spider_page.page.query_selector_all(self.selectors.wheel_brands)

        set_all = False
        for wheel_brand in wheel_brands:
            brand_name = await wheel_brand.text_content()
            if not await self.iter_brand(wheel_brand, spider_page, CategoryEnum.WHEELS):
                continue

            if not set_all:
                if brand_name.lower().strip() == 'braelin':
                    await self.set_all_results(spider_page, product_count=48)
                else:
                    set_all = await self.set_all_results(spider_page)

            product_table = await spider_page.page.query_selector(self.selectors.product_table)
            if product_table:
                soup = self.get_soup(await product_table.inner_html())
                product_rows = soup.select(self.selectors.product_rows)
                print(f"{wheel_brand} starting....")

                # For Braelin we must paginate through the 90~ pages
                # If we load all Braelin products at once then the site just crashes lol
                if brand_name.lower().strip() == 'braelin':
                    while True:
                        for product_row in product_rows:
                            wheel_data = self.scrape_wheel(product_row)
                            wheel_data['brand'] = {'brand_name': brand_name.strip()}
                            wheel_data['supplier'] = self.supplier
                            yield wheel_data

                        next_page = await spider_page.page.query_selector(self.selectors.next_page)
                        if next_page:
                            await next_page.click()
                            await spider_page.page.wait_for_selector(self.selectors.product_table, timeout=50000)
                            await self.jitter(0.5, 8)
                            continue
                        break

                else:
                    for product_row in product_rows:
                        wheel_data = self.scrape_wheel(product_row)
                        wheel_data['brand'] = {'brand_name': brand_name.strip()}
                        wheel_data['supplier'] = self.supplier
                        yield wheel_data


    def _create_wheel_name(self, wheel_name_element:SpiderTag, *wheel_details) -> str:
        """Many fastco products have the same name. This function appends some wheel data
        to the wheel name in order to make it a unique product name.
        """
        wheel_name = wheel_name_element.text.strip()
        for wheel_detail in wheel_details:
            if isinstance(wheel_detail, str):
                wheel_name += f" {wheel_detail.strip()}"
        return wheel_name
    

    def scrape_wheel_finish(self, wheel_finish_element:SpiderTag) -> str:
        """Sometimes wheel finish is in the data-original-title attribute
        and sometimes it's in the title attribute. lol
        """
        finish = wheel_finish_element.get('data-original-title')
        if not finish:
            finish = wheel_finish_element.get('title')
        if not finish:
            finish = wheel_finish_element.text
        return finish.strip()


    def _create_wheel_attribute_dict(
            self,
            diameter:str,
            width:str,
            bolt_pattern:str,
            offset:str,
            centerbore:str,
            weight:str,
            finish:str
    ) -> dict[WheelAttributeEnum, str]:
        return {
            WheelAttributeEnum.DIAMETER.value : diameter,
            WheelAttributeEnum.WIDTH.value : width,
            WheelAttributeEnum.BOLT_PATTERN.value : bolt_pattern,
            WheelAttributeEnum.OFFSET.value : offset,
            WheelAttributeEnum.CENTERBORE.value : centerbore,
            WheelAttributeEnum.WEIGHT.value : weight,
            WheelAttributeEnum.FINISH.value : finish,
        }


    def scrape_wheel(self, wheel_row:SpiderTag) -> dict:

        img_element = wheel_row.select_one(self.selectors.image)
        wheel_name_element = wheel_row.select_one(self.selectors.wheel_name)
        wheel_size_element = wheel_row.select_one(self.selectors.wheel_size)
        wheel_bolt_element = wheel_row.select_one(self.selectors.wheel_bolt_pattern)
        wheel_offset_element = wheel_row.select_one(self.selectors.wheel_offset)
        wheel_seat_element = wheel_row.select_one(self.selectors.wheel_seat)
        wheel_centerbore_element = wheel_row.select_one(self.selectors.wheel_centerbore)
        wheel_weight_element = wheel_row.select_one(self.selectors.wheel_weight)
        wheel_finish_element = wheel_row.select_one(self.selectors.wheel_finish)
        price_element = wheel_row.select_one(self.selectors.wheel_msrp)
        product_code_element = wheel_row.select_one(self.selectors.wheel_product_code)
        # inventory_qty = self.get_inventory_qty(wheel_row)
        wheel_size = wheel_size_element.text.replace(' ', '')
        wheel_diameter, wheel_width = self.parse_wheel_size(wheel_size_string = wheel_size)
        wheel_bolt_pattern = wheel_bolt_element.text.strip()
        wheel_offset = wheel_offset_element.text.strip()
        wheel_seat = wheel_seat_element.text.strip()
        wheel_centerbore = wheel_centerbore_element.text.strip()
        wheel_weight = wheel_weight_element.text.strip()
        wheel_finish = self.scrape_wheel_finish(wheel_finish_element)
        wheel_name = self._create_wheel_name(wheel_name_element, wheel_size, wheel_bolt_pattern, wheel_offset, wheel_centerbore)
        product_code = product_code_element.text

        msrp = price_element.text
        cost = self.scrape_cost(price_element)
        wheel_attributes = self._create_wheel_attribute_dict(
            diameter=wheel_diameter,
            width=wheel_width,
            bolt_pattern=wheel_bolt_pattern,
            offset=wheel_offset,
            centerbore=wheel_centerbore,
            weight=wheel_weight,
            finish=wheel_finish
        )

        data = {
            'categories': {
                'category': self.get_category_from_enum(CategoryEnum.WHEELS),
                'subcategory' : self.get_subcategory_from_enum(SubCategoryEnum.UNKNOWN)
            },
            'product': {
                'product_name': wheel_name,
                'description': None,
                'product_code': product_code,
            },
            'price': {
                'msrp': msrp,
            },
            'cost': {
                'cost': cost,
            },
            'tire_attributes' : None,
            'wheel_attributes' : wheel_attributes,
            'image_url': {
                'image_url': self.scrape_image_url(img_element)
            }
        }
        return data


    async def run(self):
        await self.start('chromium', headless=False)
        
        # Requires authentication so I don't want to use the shady-looking datacenter proxy
        spider_context = await self.new_context(stateful=False, proxy=False)
        spider_page = await spider_context.new_spider_page()
        page = spider_page.page

        res = await spider_page.goto_or_none(self.url)
        if res is None:
            self.errors.raise_http_error()
        await page.wait_for_load_state(state='load', timeout=50000)
        await self.jitter(1, 2)
        modal_close_button = await page.query_selector(self.selectors.modal_close)
        if modal_close_button:
            await modal_close_button.click()

        username_login = await page.query_selector(self.selectors.username_input)
        password_login = await page.query_selector(self.selectors.password_input)
        btn_sign_in = await page.query_selector(self.selectors.btn_sign_in)

        await username_login.type(self.USERNAME)
        await password_login.type(self.PASSWORD)
        await btn_sign_in.click()
        await page.wait_for_load_state(state='load', timeout=50000)

        print()
        print('---------------')
        print()
        cookies = await spider_context.context.cookies()
        for cookie in cookies:
            for key, value in cookie.items():
                print(key, " : ", value)
            print()

        print('---------------')
        print()
        modal_close_button = await page.query_selector(self.selectors.modal_close)
        if modal_close_button:
            await modal_close_button.click()

        # # Scrape tires:
        async for data in self.scrape_tires_by_brand(spider_page):
            if not data:
                continue
            yield data

        # # Scrape wheels:
        # async for data in self.scrape_wheels_by_brand(spider_page):
        #     yield data


        # print('starting the really long wait...')
        # await self.jitter(100000,100000)

        yield {}
        


