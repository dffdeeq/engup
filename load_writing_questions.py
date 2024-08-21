import asyncio
import json
import os.path

import pandas as pd

from src.postgres.enums import CompetenceEnum
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.settings import Settings
from src.settings.static import OTHER_DATA_DIR


async def main():
    df = pd.read_excel(os.path.join(OTHER_DATA_DIR, 'writing topics v02.xlsx'))
    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)

    async with session() as session:
        async with session.begin():
            for index, row in df.iterrows():
                question_data = {
                    'card_title': row['Essay Type'],
                    'card_body': row['Card']
                }

                new_question = Question(
                    competence=CompetenceEnum.writing,
                    question_json=json.dumps(question_data)
                )

                session.add(new_question)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
