import typing as T # noqa

from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres.enums import CompetenceEnum
from src.postgres.models.question import Question
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factory import RepoFactory
from sqlalchemy.future import select as future_select


class QuestionRepo(RepoFactory):
    def __init__(self, model: T.Type[Question], session: AsyncSession):
        super().__init__(model, session) # noqa

    async def associate_user_and_question(
            self,
            user_id: int,
            question_id: int,
            user_answer_json: T.Optional[dict] = None,
            user_result_json: T.Optional[dict] = None,
            already_complete: bool = False
    ):
        await self.insert_one(
            model=TgUserQuestion,
            user_id=user_id,
            question_id=question_id,
            user_answer_json=user_answer_json,
            user_result_json=user_result_json,
            status=already_complete
        )

    async def get_started_question_for_user(self, user_id: int, competence: CompetenceEnum) -> Question:
        subq = select(TgUserQuestion.question_id).where(TgUserQuestion.user_id == user_id, TgUserQuestion.status.is_(False))  # noqa
        stmt = future_select(Question).where(Question.id.in_(subq), Question.competence == competence, Question.is_active.is_(True))  # noqa
        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_new_question_for_user(self, user_id: int, competence: CompetenceEnum) -> Question:
        subq = select(TgUserQuestion.question_id).where(TgUserQuestion.user_id == user_id)  # noqa
        stmt = future_select(Question).where(not_(Question.id.in_(subq)), Question.competence == competence, Question.is_active.is_(True))  # noqa
        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()
