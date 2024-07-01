import asyncio
import typing as T  # noqa
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.core.filters.essay_filter import EssayFilter
from src.bot.core.states import WritingState
from src.bot.handlers.constants import MessageTemplates, DefaultMessages
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.services.factories.question import QuestionService
from src.services.factories.user_question import UserQuestionService

router = Router(name=__name__)


@router.callback_query(
    F.data.startswith('writing'),
    INJECTOR.inject_question,
    INJECTOR.inject_uq
)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    question_service: QuestionService,
    uq_service: UserQuestionService,
):
    question = await question_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.writing)
    await callback.answer()
    question_json: T.Dict = json.loads(question.question_json)
    card_title, card_body = question_json.get('card_title'), question_json.get('card_body')

    await state.set_state(WritingState.get_user_answer)
    uq_instance = await uq_service.get_or_create_user_question(
        user_id=callback.from_user.id, question_id=question.id)
    await state.set_data({
        'question_id': question.id,
        'card_body': card_body,
        'uq_id': uq_instance.id,
        'premium_queue': uq_instance.premium_queue
    })

    if not uq_instance.premium_queue:
        await callback.message.edit_text(text=DefaultMessages.DONT_HAVE_POINTS)
        await asyncio.sleep(2)

    text = MessageTemplates.CARD_TEXT_TEMPLATE.format(card_title=card_title, card_body=card_body)
    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text='Назад', callback_data='menu')]])
    await callback.message.answer(text=text, reply_markup=builder.as_markup())


@router.message(
    WritingState.get_user_answer,
    EssayFilter(),
    INJECTOR.inject_uq,
    INJECTOR.inject_gpt_producer
)
async def writing_get_user_answer(
    message: types.Message,
    state: FSMContext,
    uq_service: UserQuestionService,
    gpt_producer: GPTProducer
):
    state_data = await state.get_data()
    user_answer_json = await uq_service.format_question_answer_to_dict(state_data['card_body'], message.text)
    await uq_service.update_user_question(state_data['uq_id'], user_answer_json)
    await gpt_producer.create_task_generate_result(
        state_data['uq_id'],
        local_model=True,
        premium_queue=state_data['premium_queue']
    )
    await state.clear()
    await message.answer(text=DefaultMessages.CALCULATING_RESULT)
