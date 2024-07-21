import typing as T  # noqa

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.libs.adapter import Adapter
from src.postgres.enums import CompetenceEnum
from src.postgres.models.tg_user import TgUser
from src.postgres.models.tg_user_question import TgUserQuestion
from src.repos.factories.user import TgUserRepo
from src.repos.factories.user_question import TgUserQuestionRepo
from src.services.factory import ServiceFactory
from src.settings import Settings


class UserQuestionService(ServiceFactory):
    def __init__(
        self,
        repo: TgUserQuestionRepo,
        adapter: Adapter,
        session: async_sessionmaker,
        settings: Settings,
        user_repo: TgUserRepo
    ):
        super().__init__(repo, adapter, session, settings)
        self.repo = repo
        self.user_repo = user_repo

    async def get_or_create_user_question(self, user_id, question_id) -> TgUserQuestion:
        instance = await self.repo.get_user_question(user_id, question_id)
        if not instance:
            instance = await self.repo.create_user_question(user_id, question_id)
        if not instance.premium_queue and await self.user_repo.deduct_point(user_id):
            async with self.session() as session:
                instance.premium_queue = True
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
        return instance

    async def simple_update_uq(
        self,
        uq_id: int,
        answer_json: T.Optional[dict] = None,
        result_json: T.Optional[dict] = None,
        status: bool = False
    ):
        await self.repo.update_user_question(uq_id, answer_json, result_json, status)

    @staticmethod
    async def update_uq(session, instance: TgUserQuestion, user_result_json):
        async with session() as session:
            instance.user_result_json = user_result_json
            instance.status = True
            session.add(instance)

            user_query = await session.execute(select(TgUser).where(and_(TgUser.id == instance.user_id)))
            user = user_query.scalar_one_or_none()
            user.completed_questions += 1
            session.add(user)
            if user.completed_questions == 3 and user.referrer_id:
                referrer_query = await session.execute(
                    select(TgUser).where(and_(TgUser.id == user.referrer_id))
                )
                referrer = referrer_query.scalar_one_or_none()
                if referrer:
                    referrer.pts += 5
                    session.add(referrer)
            await session.commit()

    @staticmethod
    async def format_question_answer_to_dict(card_text: str, user_answer: str) -> T.Dict:
        return {'card_text': card_text, 'user_answer': user_answer}

    @staticmethod
    async def format_user_qa_to_answers_only(user_answer_json: T.Dict) -> str:
        return ' '.join(q['user_answer'] for part in user_answer_json.values() for q in part)

    @staticmethod
    async def format_user_qa_to_full_text(user_answer_json: T.Dict, competence: CompetenceEnum) -> str:
        if competence == CompetenceEnum.writing:
            return f"Card text: '{user_answer_json['card_text']}', response text: '{user_answer_json['user_answer']}'"
        elif competence == CompetenceEnum.speaking:
            return ' '.join(f'question: {q["card_text"]}, answer: {q["user_answer"]}.'
                            for part in user_answer_json.values() for q in part)

    @staticmethod
    async def format_user_qa_to_text_for_gpt(user_answer_json: T.Dict, competence: CompetenceEnum) -> str:
        if competence == CompetenceEnum.speaking:
            parts_text = []
            for part, questions in user_answer_json.items():
                part_num = part.split('_')[1]
                part_text = [f"Part {part_num}:\n"]
                for i, q in enumerate(questions):
                    part_text.append(f"Q: {q['card_text']}\nA: {q['user_answer']}\n")
                parts_text.append("".join(part_text))
            return "\n".join(parts_text)
        elif competence == CompetenceEnum.writing:
            return f"Card text: '{user_answer_json['card_text']}', response text: '{user_answer_json['user_answer']}'"
