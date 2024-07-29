from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.other.poll_questions import POLL_QUESTIONS
from src.bot.injector import INJECTOR
from src.services.factories.feedback import FeedbackService
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


@router.callback_query(F.data == 'leave_feedback', INJECTOR.inject_tg_user)
async def leave_feedback_callback(callback: types.CallbackQuery, state: FSMContext, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to leave feedback')

    await callback.answer()
    await state.set_data({
        'poll_questions': POLL_QUESTIONS,
        'poll_len': len(POLL_QUESTIONS),
        'current_question': 0,
        'results': []
    })
    question, options = POLL_QUESTIONS[0]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option, callback_data=f"poll_answer:0:{idx}")] for idx, option in enumerate(options)
    ])

    await callback.message.edit_text(text=question, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith('poll_answer:'),
    INJECTOR.inject_tg_user,
    INJECTOR.inject_feedback_service
)
async def handle_poll_answer(
    callback: types.CallbackQuery,
    state: FSMContext,
    tg_user_service: TgUserService,
    feedback_service: FeedbackService
):
    await callback.answer()

    _, current_question, selected_option = callback.data.split(':')
    current_question = int(current_question)
    selected_option = int(selected_option)

    state_data = await state.get_data()
    poll_questions = state_data['poll_questions']
    question, options = poll_questions[current_question]
    selected_answer = options[selected_option]

    results = state_data['results']
    results.append({'question': question, 'answer': selected_answer})
    await state.update_data({'results': results})

    next_question = current_question + 1
    if next_question < state_data['poll_len']:
        question, options = poll_questions[next_question]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"poll_answer:{next_question}:{idx}")] for idx, option in
            enumerate(options)
        ])
        await callback.message.edit_text(text=question, reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Back', callback_data='support_menu')]
        ])
        if await feedback_service.user_can_get_free_points(callback.from_user.id):
            await feedback_service.save_user_poll_feedback(callback.from_user.id, results)
            await tg_user_service.mark_user_activity(callback.from_user.id, 'left a feedback')
            await tg_user_service.add_points(callback.from_user.id, 3)
            await tg_user_service.mark_user_pts(callback.from_user.id, 'feedback', 3)
            await callback.message.edit_text(
                text="Thanks for the feedback! You have 3 more free tests",
                reply_markup=keyboard
            )
        else:
            await feedback_service.save_user_poll_feedback(callback.from_user.id, results)
            await callback.message.edit_text(
                text="Thanks for the feedback! You have already received free tests for completing the survey",
                reply_markup=keyboard
            )
