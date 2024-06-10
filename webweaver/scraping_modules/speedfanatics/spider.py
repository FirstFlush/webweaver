from pathlib import Path
from urllib.parse import urlparse, urljoin

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.soup_base import SpiderSoup, SpiderTag
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider


class SpeedFanaticsSelectors:
    ...


class SpeedFanaticsSpider(PlaywrightSpider):

    selectors = SpeedFanaticsSelectors

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.base_url = 'https://speedfanatics.ca'
        # self.base_url = 'https://speedfanatics.ca/SFMC'
        self.base_domain = urlparse(self.base_url).netloc
        self.crawled_urls = set()
        self.urls_to_crawl = set([self.base_url])
        self.speed_fanatics_dir = Path('/home/baga/speed_fanatics_clone/clone_files')
        self.speed_fanatics_dir.mkdir(exist_ok=True)


    def create_html_file(self, soup:SpiderSoup, url:str):
        url_dir_path = urlparse(url).path
        file_name = url_dir_path.replace('/', '__')
        print('file name: ', file_name)
        with open(f"{self.speed_fanatics_dir}/{file_name}.html", 'w') as f:
            f.write(soup.prettify())


    async def fetch(self, url:str) -> str:
        res = await self.aio.get_or_error(url, use_proxy=True)
        return await res.text()


    def is_same_domain(self, url:str):
        return urlparse(url).netloc == self.base_domain


    def add_urls(self, urls):
        for url in urls:
            if url not in self.crawled_urls and self.is_same_domain(url):
                self.urls_to_crawl.add(url)


    async def crawl(self, url):
        html = await self.fetch(url)
        if html:
            self.crawled_urls.add(url)
            soup = self.get_soup(html)
            self.create_html_file(soup, url)
            links = [urljoin(self.base_url, tag['href']) for tag in soup.find_all('a', href=True)]
            self.add_urls(links)


    async def run(self):
        # async with aiohttp.ClientSession() as self.session:
        while self.urls_to_crawl:
            url = self.urls_to_crawl.pop()
            print('[CRAWLING] ', url)
            await self.crawl(url)
            print(f'[OK]')
            print()
        yield {}

