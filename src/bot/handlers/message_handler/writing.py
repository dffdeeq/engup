import logging
import typing as T  # noqa
import asyncio
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.bot.core.states import WritingState
from src.bot.handlers.constants import DefaultMessages, MessageTemplates
from src.bot.handlers.utils import answer_parts_async_generator
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.services.factories.question import QuestionService
from src.services.factories.result import ResultService
from src.services.factories.user_question import UserQuestionService

router = Router(name=__name__)


@router.callback_query(F.data == 'writing', INJECTOR.inject_question, INJECTOR.inject_uq)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    question_service: QuestionService,
    uq_service: UserQuestionService,
):
    question = await question_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.writing)
    question_json: T.Dict = json.loads(question.question_json)
    card_title, card_body = question_json.get('card_title'), question_json.get('card_body')

    await state.set_state(WritingState.get_user_answer)
    uq_instance = await uq_service.get_or_create_user_question(user_id=callback.from_user.id, question_id=question.id)
    await state.set_data({'question_id': question.id, 'card_body': card_body, 'uq_id': uq_instance.id})

    text = MessageTemplates.CARD_TEXT_TEMPLATE.format(card_title=card_title, card_body=card_body)
    await callback.message.edit_text(text=text)


@router.message(WritingState.get_user_answer, INJECTOR.inject_result, INJECTOR.inject_uq)
async def writing_get_user_answer(
    message: types.Message,
    state: FSMContext,
    result_service: ResultService,
    uq_service: UserQuestionService
):
    user_answer = message.text
    if len(user_answer.split()) < 150:
        await message.answer(text=DefaultMessages.TOO_SHORT_TEXT_WARNING)
        return

    state_data = await state.get_data()
    user_answer_text = await result_service.format_question_answer_to_text(state_data['card_body'], user_answer)
    user_answer_json = await result_service.format_question_answer_to_dict(state_data['card_body'], user_answer)

    try:
        user_result = await result_service.generate_result(user_answer_text, CompetenceEnum.writing)
        if not user_result:
            await message.answer(text=DefaultMessages.ASSESSMENT_FAILURE)
            return
        await uq_service.update_user_question(state_data['uq_id'], user_answer_json, user_result.model_dump(), True)
        async for msg in answer_parts_async_generator(user_result):
            await message.answer(text=msg)
            await asyncio.sleep(3)
        general_recommendations = MessageTemplates.GENERAL_RECOMMENDATIONS_TEMPLATE.format(
            vocabulary='\n'.join(f'- {word}' for word in user_result.vocabulary)
        )
        await message.answer(text=general_recommendations)
    except Exception as e:
        logging.error(e)
