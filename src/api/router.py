from fastapi import APIRouter
from sqlalchemy import select, and_

from src.api.schemas import TranscriptionData
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.temp_data import TempData
from src.settings import Settings

router = APIRouter()


@router.post("/webhook")
async def webhook(data: TranscriptionData):
    first_file_name = data.transcriptions[0].name
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)
    async with session() as session:
        query = await session.execute(select(TempData).where(and_(TempData.first_file_name == first_file_name)))
        result = query.scalar_one_or_none()
        print(data)
        if result:
            print(result.id)
        else:
            print('No data found')
