from fastapi import HTTPException, Request
from webweaver.webscraping.campaigns.models import Campaign, ScrapeJob
from webweaver.webscraping.spiders.models import SpiderAsset



async def get_job_by_id_or_none(job_id:int=None, last:bool=False) -> ScrapeJob | None:

    if job_id or last:
        if last:
            scrape_job = await ScrapeJob.filter(is_error=False).order_by('-date_scraped').first().prefetch_related('campaign_id')
        elif job_id:
            scrape_job = await ScrapeJob.get_or_none(id=job_id).prefetch_related('campaign_id')
        if scrape_job is None:
            raise HTTPException(status_code=404, detail="Can not retrieve job.")
        return scrape_job
    else:
        return None


async def get_spider_by_id_or_none(spider_id:int = None) -> SpiderAsset | None:
    spider = await SpiderAsset.get_or_none(id=spider_id)
    if not spider:
        raise HTTPException(status_code=404, detail="Can not retrieve spider.")

    return spider


async def get_campaign_by_id_or_none(campaign_id:int = None) -> Campaign:
    campaign = await Campaign.get_or_none(id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Can not retrieve campaign.")
    return campaign


async def list_campaign(campaign_id:int = None) -> Campaign | None:
    campaign = await Campaign.get_or_none(id=campaign_id)
    if not campaign:
        return None
    return campaign