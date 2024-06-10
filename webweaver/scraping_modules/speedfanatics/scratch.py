import asyncio
import aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin



class AsyncWebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.session = None  # Will be initialized in the async context
        self.urls_to_crawl = set([base_url])
        self.crawled_urls = set()
        self.speed_fanatics_dir = Path('/home/baga/speedfanatics_scraping')
        self.speed_fanatics_dir.mkdir(exist_ok=True)


    def create_html_file(self, soup:BeautifulSoup, url:str):
        url_dir_path = urlparse(url).path
        file_name = url_dir_path.replace('/', '__')
        print('file name: ', file_name)
        with open(f"{self.speed_fanatics_dir}/{file_name}.html", 'w') as f:
            f.write(soup.prettify())


    async def fetch(self, url):
        async with self.session.get(url) as response:
            return await response.text() if response.status == 200 else None


    def is_same_domain(self, url):
        return urlparse(url).netloc == self.base_domain


    def add_urls(self, urls):
        for url in urls:
            if url not in self.crawled_urls and self.is_same_domain(url):
                self.urls_to_crawl.add(url)


    async def crawl(self, url):
        html = await self.fetch(url)
        if html:
            self.crawled_urls.add(url)
            soup = BeautifulSoup(html, 'html.parser')
            self.create_html_file(soup, url)
            links = [urljoin(self.base_url, tag['href']) for tag in soup.find_all('a', href=True)]
            self.add_urls(links)


    async def start(self):
        async with aiohttp.ClientSession() as self.session:
            while self.urls_to_crawl:
                url = self.urls_to_crawl.pop()
                print('ATTEMPTING: ', url)
                await self.crawl(url)
                print(f"Crawled: {url}")




async def main():
    crawler = AsyncWebCrawler("https://speedfanatics.ca")
    await crawler.start()



asyncio.run(main())