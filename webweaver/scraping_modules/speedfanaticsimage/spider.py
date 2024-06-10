import asyncio
from dataclasses import dataclass, asdict
import random

from webweaver.webscraping.spiders.models import SpiderAsset
from webweaver.webscraping.spiders.spider_base import PlaywrightSpider
from webweaver.modules.project_modules.speed_fanatics.models import ProductImageUrl, Product


@dataclass
class ImageData:
    product: Product
    product_image_url: ProductImageUrl
    image: bytes


class ImageScraper:

    product_image_urls:list[ProductImageUrl] = []

    def __init__(self, spider:"SpeedFanaticsImageSpider"):
        self.spider = spider

    @classmethod
    async def initialize(cls, spider:"SpeedFanaticsImageSpider") -> "ImageScraper":
        """Factory method for initializing the ImageScraper"""
        product_image_urls = await cls._product_image_urls()
        random.shuffle(product_image_urls)
        scraper = cls(spider)
        scraper.product_image_urls = product_image_urls
        if len(scraper.product_image_urls) == 0:
            scraper.spider.log("ProductImageUrl queryset has length of 0")
        return scraper


    @staticmethod
    async def _product_image_urls(limit:int=0) -> list[ProductImageUrl]:
        """Optional `limit` param for testing purposes. If you only want to grab 5 images, for example."""
        image_urls = await ProductImageUrl.filter(image_scraped=False).prefetch_related('product', 'product__supplier')
        if limit > 0:
            return image_urls[:limit]
        else:
            return image_urls


class SpeedFanaticsImageSpider(PlaywrightSpider):

    def __init__(self, spider_asset:SpiderAsset, **kwargs):
        super().__init__(spider_asset, **kwargs)
        self.url = spider_asset.domain  # this is irrelevant for this particular scraper


    async def get_image_data(self, product_image_url: ProductImageUrl) -> ImageData | None: 
        await self.jitter(0.5, 2)
        image_bytes = await self.scrape_image(product_image_url)
        if not image_bytes:
            self.log(msg=f"NO IMAGE FOUND: {product_image_url.image_url}")
            return
        else:
            image_data = ImageData(
                product = product_image_url.product,
                product_image_url=product_image_url,
                image=image_bytes,
            )
            return image_data


    async def scrape_image(self, product_image_url: ProductImageUrl) -> bytes | None:
        return await self.aio.scrape_image_url(url=product_image_url.image_url)


    async def run(self):
        image_scraper:ImageScraper = await ImageScraper.initialize()
        for product_image_url in image_scraper.product_image_urls:
            await self.jitter(0.5, 2)
            image_data = await self.get_image_data(product_image_url)
            if image_data:
                yield {'image_data': image_data}


                
            #     schema_data = {
            #         'product' : image_data.product,
            #         'product_image_url': image_data.product_image_url,
            #         'image': image_data.image,
            #     }
            #     print(schema_data['product'])
            #     print(schema_data['product_image_url'])
            #     print(bool(schema_data['image'])) 
            #     print()    

            # else:
            #     print('FAIL')
            #     print(product_image_url.image_url)
            #     print()

        # yield schema_data  

        # tasks = [self.get_image_data(product_image_url) for product_image_url in image_scraper.product_image_urls]
        # for image_data in asyncio.as_completed(tasks):
        #     awaited_data = await image_data
        #     await self.jitter(0.5, 2)
        #     if awaited_data:
        #         schema_data = {
        #             'product' : awaited_data.product,
        #             'product_image_url': awaited_data.product_image_url,
        #             'image': awaited_data.image,
        #         }
        #         yield schema_data