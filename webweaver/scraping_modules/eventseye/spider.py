import asyncio
import random
import re
from playwright.async_api import ElementHandle
from urllib.parse import urljoin

from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.webscraping.spiders.soup_base import SpiderTag, SpiderSoup
from webweaver.webscraping.spiders.models import SpiderAsset

class EventsEyeSelectors:

    #index page
    table = "table.tradeshows"    
    tradeshow_rows = ".tradeshows tbody tr"
    event_link = "td:first-of-type > a"
    city_and_state = "td:nth-of-type(3) > a.city"
    date_and_duration = "td:last-of-type"
    duration = "i"
    next_button = ".pages-links > div:nth-of-type(2) > a"
    country_backup = "td:nth-of-type(3)"
    #organizer
    organizers = ".org"
    organizer_name = "a.orglink"
    organizer_phone = ".ev-phone"
    organizer_website = "a.ev-web"
    organizer_email = "a.ev-mail"
    #venue
    venue_name = ".venue a.placelink"
    #event
    event_name = "h1"
    description = ".description"
    cycle = ".cycle"
    audience = ".audience"
    country = ".venues a.countrylink"
    industries = ".industries a"
    event_email = ".more-info a.ev-mail" #href drop 'mailto:'
    event_website = ".more-info a.ev-web" #href


class EventsEyeSpider(PlaywrightSpider):
    
    selectors = EventsEyeSelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        # self.url = 'https://www.eventseye.com/fairs/z1_trade-shows_europe_41.html'
        # self.url = 'https://www.eventseye.com/fairs/z1_trade-shows_europe_92.html'
        # self.url = 'https://www.eventseye.com/fairs/z1_trade-shows_africa-middle-east.html'
        # self.url = 'https://www.eventseye.com/fairs/z1_trade-shows_asia-pacific_41.html'
        self.url = 'https://www.eventseye.com/fairs/z1_trade-shows_america_30.html'


    async def run(self):

        await self.start('chromium', headless=True)
        spider_context = await self.new_context(stateful=False)
        spider_page = await spider_context.new_spider_page()

        page = spider_page.page
        res = await spider_page.navigation.goto_or_none(self.url)
        if res is None:
            return
        
        while True:
            await page.wait_for_load_state(state='load', timeout=100000)
            await page.wait_for_selector(self.selectors.table)
            trade_show_rows = await page.query_selector_all(self.selectors.tradeshow_rows)
            self.shuffle(trade_show_rows)
            base_url = page.url

            tasks = [self.scrape_record(trade_show_row, base_url) for trade_show_row in trade_show_rows]
            for future in asyncio.as_completed(tasks):
                yield await future

            next_button = await page.query_selector(self.selectors.next_button)
            if next_button:
                await spider_page.click_link(next_button, verbose=True)
            else:
                break


    async def scrape_record(self, trade_show_row:ElementHandle, base_url:str):
        await asyncio.sleep(random.uniform(1, 3))
        outer_soup = self.get_soup(await trade_show_row.inner_html())
        href = outer_soup.select_one(self.selectors.event_link)['href']
        absolute_url = urljoin(base_url, href)
        date, duration_days = self.get_date_and_duration(
            outer_soup.select_one(self.selectors.date_and_duration)
        )
        try:
            city, state = self.get_city_and_state(
                outer_soup.select_one(self.selectors.city_and_state)
            )
        except AttributeError:
            city, state = (None, None)

        new_spider_context = await self.new_context(stateful=False)
        new_spider_page = await new_spider_context.new_spider_page()
        new_page = new_spider_page.page
        res = await new_spider_page.goto_or_none(absolute_url)
        if res is None:
            return
        await new_page.wait_for_load_state(state='load', timeout=100000)

        soup = self.get_soup(await new_page.inner_html('body'))
        scraped_data = self.scrape_data(soup)
        if scraped_data is None:
            return
        scraped_data['venue']['city'] = city
        scraped_data['venue']['state'] = state
        scraped_data['event']['date'] = date
        scraped_data['event']['duration_days'] = duration_days
        # await self.random_delay(2, 7)
        await new_page.close()

        if scraped_data['venue']['venue_name'] is None:
            scraped_data['venue'] = None

        if scraped_data['event']['country'] is None:
            try:
                country_element = outer_soup.select_one(self.selectors.country_backup)
                country = re.search(r'\((.*?)\)', country_element.text).group(1)
            except AttributeError:
                return
            else:
                scraped_data['event']['country'] = country
        return scraped_data


    def scrape_data(self, soup:SpiderSoup) -> dict:

        print(soup.select_one(self.selectors.event_name).text.strip())

        description_element = soup.select_one(self.selectors.description)
        cycle_element = soup.select_one(self.selectors.cycle)
        audience_element = soup.select_one(self.selectors.audience)
        try:
            venue_name = soup.select_one(self.selectors.venue_name).text
        except AttributeError:
            venue_name = None

        event_email = soup.select_one_attr(self.selectors.event_email, 'href', strip_text='mailto:')
        event_website = soup.select_one_attr(self.selectors.event_website, 'href')
        try:
            country = soup.select_one(self.selectors.country).text
        except AttributeError as e:
            self.log(self.errors.ElementNotFound(e))
            country = None
        
        industries = [{'industry_name': industry_element.text} 
                      for industry_element in soup.select(self.selectors.industries)]

        organizers = []
        organizer_elements = soup.select(self.selectors.organizers)
        for organizer in organizer_elements:
            d = {}
            d['organizer_name'] = organizer.select_one_text(self.selectors.organizer_name)
            d['phone'] = organizer.select_one_text(self.selectors.organizer_phone)
            email = organizer.select_one_attr(self.selectors.organizer_email, 'href', strip_text='mailto:')
            # eventseye has screwy html. if theres no email it just appears as hidden <a href="mailto:"> tag lol
            if email == '':
                email = None
            d['email'] = email
            d['website'] = organizer.select_one_attr(self.selectors.organizer_website, 'href')
            organizers.append(d)

        description_element.select_one_and_decompose('h2')
        cycle_element.select_one_and_decompose('h2')
        audience_element.select_one_and_decompose('h2')

        data = {
            'organizers': organizers,
            'venue': {
                'venue_name': venue_name,
            },
            'event': {
                'event_name': soup.select_one(self.selectors.event_name).text.strip(),
                'description': description_element.text.strip(),
                'cycle': cycle_element.text.strip(),
                'audience': audience_element.text,
                'email': event_email,
                'website': event_website,
                'country' : country,
            },
            'industries': industries
        }

        return data


    def get_date_and_duration(self, date_and_duration:SpiderTag) -> tuple[str, str|None]:
        """Returns a tuple of the date and duration values.
        The "select_and_decompose" method is used because sometimes this element contains
        an extra <i> tag if the event is marked as 'postponed'
        """
        duration_tag = date_and_duration.select_one_and_extract('i')
        duration = duration_tag.text if duration_tag else None
        date_and_duration.select_and_decompose('i')
        date = date_and_duration.text.strip()
        return date, duration


    def get_city_and_state(self, city_state_element:SpiderTag) -> tuple[str|None, str|None]:

        tup = city_state_element.text.split('(')[0].split(',')
        city = tup[0].strip()
        try:
            state = tup[1].strip()
        except IndexError:
            state = None
        return city, state
    









        #----------------------------------------------------------

        # await self.start('chromium', headless=True)
        # print('start complete')
        # spider_context = await self.new_context(stateful=False)
        # print('created context')
        # spider_page = await spider_context.new_spider_page()
        # print('created page')
        # print()

        # page = spider_page.page
        # res = await spider_page.navigation.goto_or_none(self.url)


        # print(f'res status code: {res.status}')
        # if res is None:
        #     print('res is none')
        #     print(self.url)
        #     return
        # print('receievd response: ', res.status)
        
        # while True:
        #     await page.wait_for_load_state(state='load', timeout=30000)
        #     await page.wait_for_selector(self.selectors.table)
        #     trade_show_rows = await page.query_selector_all(self.selectors.tradeshow_rows)
        #     self.shuffle(trade_show_rows)
        #     base_url = page.url

        #     for trade_show_row in trade_show_rows:
        #         outer_soup = self.get_soup(await trade_show_row.inner_html())
        #         href = outer_soup.select_one(self.selectors.event_link)['href']
        #         absolute_url = urljoin(base_url, href)
        #         date, duration_days = self.get_date_and_duration(
        #             outer_soup.select_one(self.selectors.date_and_duration)
        #         )
        #         try:
        #             city, state = self.get_city_and_state(
        #                 outer_soup.select_one(self.selectors.city_and_state)
        #             )
        #         except AttributeError:
        #             city, state = (None, None)

        #         new_spider_context = await self.new_context(stateful=False)
        #         new_spider_page = await new_spider_context.new_spider_page()
        #         new_page = new_spider_page.page
        #         res = await new_spider_page.goto_or_none(absolute_url)
        #         if res is None:
        #             continue
        #         await new_page.wait_for_load_state(state='load', timeout=30000)

        #         soup = self.get_soup(await new_page.inner_html('body'))
        #         scraped_data = self.scrape_data(soup)
        #         if scraped_data is None:
        #             continue
        #         scraped_data['venue']['city'] = city
        #         scraped_data['venue']['state'] = state
        #         scraped_data['event']['date'] = date
        #         scraped_data['event']['duration_days'] = duration_days
        #         # await self.random_delay(2, 7)
        #         await new_page.close()

        #         if scraped_data['venue']['venue_name'] is None:
        #             scraped_data['venue'] = None

        #         if scraped_data['event']['country'] is None:
        #             try:
        #                 country_element = outer_soup.select_one(self.selectors.country_backup)
        #                 country = re.search(r'\((.*?)\)', country_element.text).group(1)
        #             except AttributeError:
        #                 continue
        #             else:
        #                 scraped_data['event']['country'] = country
        #         yield scraped_data

        #     next_button = await page.query_selector(self.selectors.next_button)
        #     if next_button:
        #         await spider_page.click_link(next_button, verbose=True)
        #     else:
        #         break