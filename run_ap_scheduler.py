import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text, and_, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from data.other.weekly_update_sql import WEEKLY_UPDATE_SQL
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.subscription import Subscription
from src.settings import Settings


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def weekly_task(_session: async_sessionmaker):
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


async def update_subscriptions(_session: async_sessionmaker):
    current_time = datetime.utcnow()
    logging.info(current_time)

    async with _session() as session:
        stmt = (
            update(Subscription)
            .where(and_(Subscription.end_date < current_time, Subscription.status == 'active'))
            .values(status='expired')
        )
        logging.info(stmt)
        await session.execute(stmt)
        await session.commit()


settings = Settings.new()
session = initialize_postgres_pool(settings.postgres)
scheduler = AsyncIOScheduler()
scheduler.add_job(weekly_task, 'cron', day_of_week='mon', hour=4, minute=1, args=(session,))
scheduler.add_job(update_subscriptions, 'interval', minutes=1, args=[session])
scheduler.start()
asyncio.get_event_loop().run_forever()
