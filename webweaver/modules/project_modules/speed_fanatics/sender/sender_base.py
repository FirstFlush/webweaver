from tortoise import Tortoise
import asyncio
import logging
import requests
from typing import TYPE_CHECKING
from webweaver.config import all_models, POSTGRES_DB


logger = logging.getLogger('sending')


class SenderBase:

    @staticmethod
    async def _db_connect():

        if POSTGRES_DB is None:
            logger.error('This script must be called from the project root directory, otherwise your env vars will all be None.')
            logger.error(f"env var POSTGRES_DB: `{POSTGRES_DB}` lol")
            return
        await Tortoise.init(db_url=POSTGRES_DB, modules={'models': all_models})
        logger.info("Connected to DB")



