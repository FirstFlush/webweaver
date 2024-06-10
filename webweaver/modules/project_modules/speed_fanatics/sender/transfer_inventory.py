
# Speed-Fanatics script for transferring product inventory DB data from 
# the webscraping app's DB to the store app's DB.
# Using requests instead of aiohttp to send the requests since receiver is
# not async. I'm not sure if it makes a difference, but it's one less thing
# to worry about.
# ---------------------------------------------------------------------------
import asyncio

import logging
import requests
from typing import TYPE_CHECKING

from webweaver.modules.project_modules.speed_fanatics.constants import URL_RECEIVER
from webweaver.modules.project_modules.speed_fanatics.sender.sender_base import SenderBase
from webweaver.modules.project_modules.speed_fanatics.sender.sender_strategies import *

if TYPE_CHECKING:
    from webweaver.webscraping.models import ScrapeModel


logger = logging.getLogger('sending')


class Sender(SenderBase):
    """This class handles the sending of DB data to the store.
    TABLES_ORDERED is a list, in order, of the tables that will be
    transferred one-by-one to the store.
    """
    URL_RECEIVER = URL_RECEIVER
    send_strategies:tuple[SenderStrategy] = (
        SupplierSendStrategy,
        BrandSendStrategy,
        CategorySendStrategy,
        SubCategorySendStrategy,
        ProductSendStrategy,
        VariationTypeSendStrategy,
        ProductVariationSendStrategy,
        TireAttributeSendStrategy,
        WheelAttributeSendStrategy,
        CostSendStrategy,

        # ProductImageSendStrategy,
    )


    async def get_data(self, strategy:SenderStrategy) -> list[dict[str, Any]]:
        
        strategy.model.all().values(*strategy.values)


    async def send(self):
        # send model/table data in order
        for strategy_class in self.send_strategies:
            strategy = await strategy_class.select_strategy()
            res = requests.post(self.URL_RECEIVER, json=self.json_data(strategy))
            logger.info(f"Status: {res.status_code} \t Model: `{strategy.model.__name__}` ")
            if res.status_code != 200:
                logger.info(f"Exiting upon status `{res.status_code}`...")
                return


    def json_data(self, strategy:SenderStrategy) -> dict[str, Any]:
        """No need to actually serialize, since this is being passed into requests.post() as json param. 
        Requests library will handle serialization.
        """
        return {
            "label": strategy.label.value,
            "data": strategy.rows,
        }


    @classmethod
    async def send_data(cls):
        sender = cls()
        await sender._db_connect()
        logger.info("Fetching table data...")
        await sender.send()


if __name__ == '__main__':
    asyncio.run(Sender.send_data())
