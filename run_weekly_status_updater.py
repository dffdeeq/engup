import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.weekly_update_sql import WEEKLY_UPDATE_SQL
from src.postgres.factory import initialize_postgres_pool
from src.settings import Settings


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def task(_session: async_sessionmaker):
    async with _session() as session:
        logging.info('Starting')
        try:
            await session.execute(text(WEEKLY_UPDATE_SQL))
            await session.commit()
            logging.info('Success')
        except Exception as e:
            logging.error(e)
            await session.rollback()


def schedule_jobs(scheduler, session: async_sessionmaker):
    trigger = CronTrigger(day_of_week='sun', hour=20, minute=0)
    scheduler.add_job(func=task, trigger=trigger, args=(session, ))


async def main():
    scheduler = AsyncIOScheduler()

    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)

    schedule_jobs(scheduler, session)
    scheduler.start()
    while True:
        await asyncio.sleep(1000)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
