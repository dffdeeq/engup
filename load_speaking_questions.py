import asyncio
import json
import os

from src.postgres.enums import CompetenceEnum
from src.postgres.factory import initialize_postgres_pool
from src.postgres.models.question import Question
from src.settings import Settings
from src.settings.static import OTHER_DATA_DIR


async def main():
    json_file_path = os.path.join(OTHER_DATA_DIR, 'new_speaking_questions_1.json')
    with open(json_file_path, 'r', encoding='utf-8') as file:
        new_questions = json.load(file)

    settings = Settings.new()
    session = initialize_postgres_pool(settings.postgres)

    async with session() as session:
        async with session.begin():
            for question_data in new_questions:
                new_question = Question(
                    competence=CompetenceEnum.speaking,
                    question_json=json.dumps(question_data),
                    is_active=True
                )

                session.add(new_question)

        await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
