from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
# from webscraping.scratch3 import bleh2 as bleh


class GoogleMapsSelectors:

    search_input = '#searchboxinput'
    # listings = '.bfdHYd.Ppzolf.OFBs3e, .bfdHYd.Ppzolf.OFBs3e.Jv9l1d'
    # listings = '.Nv2PK.THOPZb.CpccDe'
    listings = '.Nv2PK.tH5CWc.THOPZb'  #TODO: get a better listings selector
    company_name = '.qBF1Pd.fontHeadlineSmall'
    review_score = '.ZkP5Je > .MW4etd'
    review_count = '.ZkP5Je > .UY7F9'
    address = '.W4Efsd > span:last-of-type > span:last-of-type'
    phone = '.W4Efsd:last-of-type .UsdlK'
    url = 'a.lcr4fd.S9kvJb'
    
    listing_link = 'a.hfpxzc'


class GoogleMapsSpider(PlaywrightSpider):

    selectors = GoogleMapsSelectors
    # url = "https://maps.google.com"


    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)

        self.search_string = self.params['search']
        # self.search_string = "bakery vancouver"
        self.results_div = f'div[aria-label="Results for {self.search_string}"]'

    async def run(self):

        await self.start('chrome', headless=True)
        spider_context = await self.new_context(stateful=False)
        spider_page = await spider_context.new_spider_page()

        page = spider_page.page

        res = await spider_page.goto_or_none(self.url)
        if res is None:
            return
        search_input = await page.query_selector(self.selectors.search_input)
        await search_input.fill(self.search_string)
        await search_input.press('Enter')
        await page.wait_for_selector(self.results_div)
        await spider_page.infinite_scroll(self.results_div, 5000)
        results_container = await page.query_selector(self.results_div)


        listings = await page.query_selector_all(self.selectors.listings)
        first_listing = listings[0]
        test_url = await first_listing.query_selector(self.selectors.url)
        if not test_url:
            for listing in listings:
                company_name_element = await listing.query_selector(self.selectors.company_name)
                company_name_text = await company_name_element.text_content()
                print('company name: ', company_name_text)
                anchor = await listing.query_selector("a.hfpxzc")
                await anchor.click()
                popout_selector = f'.m6QErb.WNBkOb[aria-label="{company_name_text}"]'
                await page.wait_for_selector(popout_selector)
                company_url_element = await page.query_selector('.rogA2c.ITvuef .Io6YTe.fontBodyMedium.kR99db')
                company_url = await company_url_element.text_content()
                print('company url: ', company_url)
                print()
                await self.random_delay(2, 8)


        sp = self.get_soup(markup=await results_container.inner_html())
        if sp is None:
            print('ummm wheres the soup? lol')
            exit(1)


        listings = sp.select(self.selectors.listings)
        for listing in listings:
            # company_name = listing.get('aria-label')
            company_name = listing.spider_text(self.selectors.company_name)
            review_score = listing.spider_text(self.selectors.review_score, '0.0')
            review_count = listing.spider_text(self.selectors.review_count, '(0)')
            address = listing.spider_text(self.selectors.address)
            phone = listing.spider_text(self.selectors.phone)
            url = listing.spider_attribute(self.selectors.url, 'href')

            if url is None:
                pop_out_link = listing.find(self.selectors.listing_link)
                pop_out_link

            data = {
                'company': {
                    'company_name': company_name,
                    'address': address,
                    'phone': phone,
                    'url': url,
                },
                'review': {
                    'review_score': review_score,
                    'review_count': review_count,
                }
            }

            # return data
            yield data


            



        # emails = sp.find_emails(sp.flatten_html(), 'cooperdooper')
        # print('emails: ', emails)
        # print('------------------------------')
        # for link in sp.href_links('https://googleadservices.com'):
        #     print(link)
        #     print()
        # print('------------------------------')
        
