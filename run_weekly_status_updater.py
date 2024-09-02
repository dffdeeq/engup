import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.weekly_update_sql import WEEKLY_UPDATE_SQL
from src.postgres.factory import initialize_postgres_pool
from src.settings import Settings


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def task(_session: async_sessionmaker):
    async with _session() as session:
        async with session.begin():
            logging.info('Starting')
            try:
                await session.execute(text(WEEKLY_UPDATE_SQL))
                await session.commit()
                logging.info('Success')
            except Exception as e:
                logging.error(e)
                await session.rollback()

settings = Settings.new()
session = initialize_postgres_pool(settings.postgres)
scheduler = AsyncIOScheduler()
scheduler.add_job(task, 'cron', day_of_week='mon', hour=14, minute=59, args=(session, ))
scheduler.start()
asyncio.get_event_loop().run_forever()
