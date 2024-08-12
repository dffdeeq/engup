import asyncio
import typing as T  # noqa
import json

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.core.filters.essay_filter import EssayFilter
from src.bot.core.states import WritingState
from src.bot.constants import MessageTemplates, DefaultMessages
from src.bot.injector import INJECTOR
from src.postgres.enums import CompetenceEnum
from src.rabbitmq.producer.factories.gpt import GPTProducer
from src.services.factories.question import QuestionService
from src.services.factories.tg_user import TgUserService
from src.services.factories.user_question import UserQuestionService

router = Router(name=__name__)


@router.callback_query(
    F.data.startswith('writing'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_question,
    INJECTOR.inject_uq
)
async def writing_start(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    question_service: QuestionService,
    uq_service: UserQuestionService,
):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'start writing')

    question = await question_service.get_or_generate_question_for_user(callback.from_user.id, CompetenceEnum.writing)
    question_json: T.Dict = json.loads(question.question_json)
    card_title, card_body = question_json.get('card_title'), question_json.get('card_body')

    await state.set_state(WritingState.get_user_answer)
    uq_instance = await uq_service.get_or_create_user_question(
        user_id=callback.from_user.id, question_id=question.id)
    await state.set_data({
        'question_id': question.id,
        'card_body': card_body,
        'uq_id': uq_instance.id,
    })

    await callback.message.edit_text(text=DefaultMessages.DEFAULT_TEXT)
    await asyncio.sleep(2)
    text = MessageTemplates.CARD_TEXT_TEMPLATE.format(card_title=card_title, card_body=card_body)
    builder = InlineKeyboardBuilder([[InlineKeyboardButton(text='🔙 Back', callback_data='ielts_menu')]])
    await callback.message.answer(text=text, reply_markup=builder.as_markup())


@router.message(
    WritingState.get_user_answer,
    EssayFilter(),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_uq,
    INJECTOR.inject_gpt_producer
)
async def writing_get_user_answer(
    message: types.Message,
    state: FSMContext,
    uq_service: UserQuestionService,
    tg_user_service: TgUserService,
):
    user = await tg_user_service.get_or_create_tg_user(message.from_user.id)
    await tg_user_service.mark_user_activity(message.from_user.id, 'end writing')
    state_data = await state.get_data()
    await state.set_state(WritingState.ending)
    user_answer_json = await uq_service.format_question_answer_to_dict(state_data['card_body'], message.text)
    await state.update_data({'user_answer_json': user_answer_json, 'task_ready_to_proceed': 'writing'})

    if user.pts >= 1:
        text = ('Thank you for completing all the questions! To confirm your response, '
                'please choose one of the following options:\n\n'
                '1. Use 1 PT to receive a detailed analysis\n'
                '2. Receive a brief result without charge.')
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='1', callback_data='confirm_task_writing premium')],
            [InlineKeyboardButton(text='2', callback_data='confirm_task_writing default')],
        ])

    else:
        text = ('You do not have any Premium Tests (PTs) left in your account.\n\n'
                'If you would like to spend 1 PT and receive a detailed analysis and '
                'personalized recommendations based on your answers, please purchase some PTs, then go back and'
                'click on "Update PTs" button for proceed test in premium')
        builder = InlineKeyboardBuilder([
            [InlineKeyboardButton(text='Buy PTs', callback_data='pricing')],
            [InlineKeyboardButton(text='Proceed for free', callback_data='confirm_task_writing default')],
        ])
    await message.answer(text, reply_markup=builder.as_markup())


@router.callback_query(
    F.data.startswith('confirm_task_writing'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_uq,
    INJECTOR.inject_gpt_producer
)
async def writing_confirm_task(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    uq_service: UserQuestionService,
    gpt_producer: GPTProducer
):
    param = callback.data.split()[1]
    premium = True if param == 'premium' else False

    state_data = await state.get_data()
    if premium is True:
        await tg_user_service.repo.deduct_point(callback.from_user.id)
        await tg_user_service.mark_user_activity(callback.from_user.id, 'spent point')
        await tg_user_service.mark_user_pts(callback.from_user.id, 'spent', -1)

    user_answer_json = state_data['user_answer_json']
    await uq_service.simple_update_uq(state_data['uq_id'], user_answer_json)
    await gpt_producer.create_task_generate_result(state_data['uq_id'], premium)
    await callback.message.edit_text(text=DefaultMessages.CALCULATING_RESULT)
    await state.clear()
