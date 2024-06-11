import typing as T  # noqa
import asyncio
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from src.bot.core.states import WritingState
from src.bot.handlers.constants import Messages, MessageTemplates
from src.bot.handlers.utils import answer_parts_async_generator
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.services.factories.gpt import GPTService

router = Router(name=__name__)


@router.callback_query(F.data == 'writing', INJECTOR.inject_tg_bot, INJECTOR.inject_gpt)
async def writing_start(callback: types.CallbackQuery, state: FSMContext, gpt_service: GPTService):
    question = await gpt_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.writing)
    question_json: T.Dict = json.loads(question.question_json)
    card_title, card_body = question_json.get('card_title'), question_json.get('card_body')

    await state.set_state(WritingState.get_user_answer)
    await state.set_data({'question_id': question.id, 'card_body': card_body})

    text = MessageTemplates.CARD_TEXT_TEMPLATE.format(card_title=card_title, card_body=card_body)
    await callback.message.edit_text(text=text)


@router.message(WritingState.get_user_answer, INJECTOR.inject_tg_bot, INJECTOR.inject_gpt)
async def writing_get_user_answer(message: types.Message, state: FSMContext, gpt_service: GPTService):
    user_answer = message.text
    if len(user_answer.split()) < 150:
        await message.answer(text=Messages.TOO_SHORT_TEXT_WARNING)
        return

    state_data = await state.get_data()
    question_id, card_body = state_data['question_id'], state_data['card_body']

    user_answer_text = await gpt_service.format_user_answer_to_text_request(card_body, user_answer)
    user_answer_json = await gpt_service.format_user_answer_to_dict(card_body, user_answer)
    user_result = await gpt_service.try_generate_result(user_answer_text, CompetenceEnum.writing, 3)
    if not user_result:
        await message.answer(text=Messages.ASSESSMENT_FAILURE)
        return

    await gpt_service.link_user_with_question(
        user_id=message.from_user.id,
        question_id=int(question_id),
        user_answer_json=user_answer_json,
        user_result_json=user_result.model_dump(),
        already_complete=True
    )

    async for msg in answer_parts_async_generator(user_result):
        await message.answer(text=msg)
        await asyncio.sleep(3)

    general_recommendations = MessageTemplates.GENERAL_RECOMMENDATIONS_TEMPLATE.format(
        vocabulary='\n'.join(f'- {word}' for word in user_result.vocabulary)
    )
    await message.answer(text=general_recommendations)
