from webweaver.webscraping.spiders.spider_base import PlaywrightSpider


class GoogleMapsSelectors:

    search_input = '#searchboxinput'
    listings = '.bfdHYd.Ppzolf.OFBs3e, .bfdHYd.Ppzolf.OFBs3e.Jv9l1d'
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


    def __init__(self, spider_id:int, domain:str, **kwargs):
        super().__init__(spider_id, domain, **kwargs)

        self.search_string = self.params['search']
        self.results_div = f'div[aria-label="Results for {self.search_string}"]'

    async def run(self):

        await self.start('chrome', headless=False)
        res = await self.goto(self.url)
        if res is None:
            return
        search_input = await self.page.query_selector(self.selectors.search_input)
        await search_input.fill(self.search_string)
        await search_input.press('Enter')
        await self.page.wait_for_selector(self.results_div)
        # await self.infinite_scroll(self.results_div, 5000)
        results_container = await self.page.query_selector(self.results_div)

        data = {}



        # sp = self.get_parser(markup=await results_container.inner_html())
        # if sp is None:
        #     print('ummm wheres the parser? lol')
        #     exit(1)


        # listings = sp.select(self.selectors.listings)
        # for listing in listings:
        #     # company_name = listing.get('aria-label')
        #     company_name = listing.spider_text(self.selectors.company_name)
        #     review_score = listing.spider_text(self.selectors.review_score, '0.0')
        #     review_count = listing.spider_text(self.selectors.review_count, '(0)')
        #     address = listing.spider_text(self.selectors.address)
        #     phone = listing.spider_text(self.selectors.phone)
        #     url = listing.spider_attribute(self.selectors.url, 'href')

        #     if url is None:
        #         pop_out_link = listing.find(self.selectors.listing_link)
        #         pop_out_link

            # data = {
            #     'company': {
            #         'company_name': company_name,
            #         'address': address,
            #         'phone': phone,
            #         'url': url,
            #     },
            #     'review': {
            #         'review_score': review_score,
            #         'review_count': review_count,
            #     }
            # }

        return data


            



        # emails = sp.find_emails(sp.flatten_html(), 'cooperdooper')
        # print('emails: ', emails)
        # print('------------------------------')
        # for link in sp.href_links('https://googleadservices.com'):
        #     print(link)
        #     print()
        # print('------------------------------')
        
