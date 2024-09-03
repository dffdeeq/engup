from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.other.poll_questions import POLL_QUESTIONS, ADVANCED_POLL_QUESTIONS
from src.bot.core.states import FeedbackState
from src.bot.injector import INJECTOR
from src.services.factories.feedback import FeedbackService
from src.services.factories.tg_user import TgUserService

router = Router(name=__name__)


async def write_poll_results(survey_type: str, tg_user_service, feedback_service, user_id, results) -> str:
    free_pts = 2 if survey_type == 'advanced' else 1
    await tg_user_service.mark_user_activity(user_id, f'end the {survey_type} survey')
    if await feedback_service.user_can_get_free_points(user_id, survey_type):
        await feedback_service.save_user_poll_feedback(user_id, results, survey_type)
        await tg_user_service.add_points(user_id, free_pts)
        await tg_user_service.mark_user_activity(user_id, 'add feedback free pt')
        await tg_user_service.mark_user_pts(user_id, 'feedback', free_pts)
        return f'Thanks for the feedback! You have {free_pts} more free tests'
    else:
        await feedback_service.save_user_poll_feedback(user_id, results)
        return 'Thanks for the feedback! You have already received free tests for completing the survey'


@router.callback_query(F.data == 'feedback_menu', INJECTOR.inject_tg_user)
async def feedback_menu_callback(callback: types.CallbackQuery, tg_user_service: TgUserService):
    await tg_user_service.mark_user_activity(callback.from_user.id, 'go to feedback menu')
    await callback.answer()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⭐️ Rate us', callback_data="rate_bot start")],
        [InlineKeyboardButton(text='☑️ Take the survey', callback_data="take_the_survey new")],
        [InlineKeyboardButton(text='✅ Take the advanced survey', callback_data="take_the_survey advanced")],
        [InlineKeyboardButton(text='🔙 Back', callback_data='menu'), ],
    ])
    await callback.message.edit_text(text='Here you can leave a feedback', reply_markup=keyboard)


@router.callback_query(F.data.startswith('rate_bot'), INJECTOR.inject_tg_user)
async def rate_bot_callback(callback: types.CallbackQuery, state: FSMContext, tg_user_service: TgUserService):
    rate = callback.data.split()[1]
    if rate == 'start':
        await tg_user_service.mark_user_activity(callback.from_user.id, 'go to rate us')
        await callback.answer()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'{i}', callback_data=f"rate_bot {i}") for i in range(1, 6)]
        ])
        await callback.message.edit_text(text='"Please rate your experience with the bot from 1 to 5, '
                                              'where 1 is poor and 5 is excellent.', reply_markup=keyboard)
    else:
        rate = int(rate)
        await state.set_state(FeedbackState.get_user_review)
        await state.set_data({'rate': rate})
        await callback.message.edit_text(text='Thank you for your rating! Please type your feedback or suggestions in '
                                              'the message to help us improve your experience.')


@router.message(
    FeedbackState.get_user_review,
    INJECTOR.inject_tg_user,
    INJECTOR.inject_feedback_service
)
async def feedback_get_review_callback(
    message: types.Message,
    state: FSMContext,
    tg_user_service: TgUserService,
    feedback_service: FeedbackService
):
    await tg_user_service.mark_user_activity(message.from_user.id, 'rate completed')
    rate = (await state.get_data())['rate']
    text = message.text
    await feedback_service.save_user_review(message.from_user.id, rate, text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Menu', callback_data='menu'), ],
    ])

    await message.answer(text='Thank you! We have received your feedback and appreciate your input.',
                         reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data.startswith('take_the_survey'), INJECTOR.inject_tg_user)
async def leave_feedback_callback(callback: types.CallbackQuery, state: FSMContext, tg_user_service: TgUserService):
    survey_type = callback.data.split()[1]

    if survey_type == 'advanced':
        user = await tg_user_service.get_or_create_tg_user(callback.from_user.id)
        if user.completed_questions < 3:
            await callback.answer(text='You must take at least three tests to complete this survey', show_alert=True)
            return
    await tg_user_service.mark_user_activity(
        callback.from_user.id,
        f'go to take the {survey_type} survey'
    )

    poll_questions = ADVANCED_POLL_QUESTIONS if survey_type == 'advanced' else POLL_QUESTIONS

    await callback.answer()
    await state.set_data({
        'poll_questions': poll_questions,
        'poll_len': len(poll_questions),
        'current_question': 0,
        'results': [],
        'survey_type': survey_type,
    })
    question, options = poll_questions[0]
    if len(options) < 1:
        await state.set_state(FeedbackState.get_other_option)
        await state.update_data({'question_for_another_option': question, 'current_question': 0})
        await callback.message.edit_text(text=f'{question}\n\nWrite your detailed answer')
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option, callback_data=f"poll_answer:0:{idx}")] for idx, option in enumerate(options)
    ] + [[InlineKeyboardButton(text='🔙 Back', callback_data='feedback_menu')
          ]])

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
    survey_type = state_data['survey_type']
    poll_questions = state_data['poll_questions']
    question, options = poll_questions[current_question]
    selected_answer = options[selected_option]

    if selected_answer == 'Other':
        await state.set_state(FeedbackState.get_other_option)
        await state.update_data({'question_for_another_option': question, 'current_question': current_question})
        await callback.message.edit_text(text=f'{question}\n\nWrite your detailed answer')
        return

    results = state_data['results']
    results.append({'question': question, 'answer': selected_answer})
    await state.update_data({'results': results})

    next_question = current_question + 1
    if next_question == 1:
        await tg_user_service.mark_user_activity(callback.from_user.id, f'start the {survey_type} survey')
    if next_question < state_data['poll_len']:
        question, options = poll_questions[next_question]
        if len(options) < 1:
            await state.set_state(FeedbackState.get_other_option)
            await state.update_data({'question_for_another_option': question, 'current_question': next_question})
            await callback.message.edit_text(text=f'{question}\n\nWrite your detailed answer')
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"poll_answer:{next_question}:{idx}")] for idx, option in
            enumerate(options)
        ])
        await callback.message.edit_text(text=question, reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Back', callback_data='support_menu')]
        ])

        text = await write_poll_results(survey_type, tg_user_service, feedback_service, callback.from_user.id, results)
        await state.clear()
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard
        )


@router.message(
    FeedbackState.get_other_option,
    INJECTOR.inject_tg_user,
    INJECTOR.inject_feedback_service
)
async def feedback_get_other_option(
    message: types.Message,
    state: FSMContext,
    tg_user_service: TgUserService,
    feedback_service: FeedbackService
):
    state_data = await state.get_data()
    survey_type = state_data['survey_type']
    question = state_data['question_for_another_option']
    results = state_data['results']
    current_question = state_data['current_question']
    poll_questions = state_data['poll_questions']
    results.append({'question': question, 'answer': message.text})
    await state.update_data({'results': results})

    next_question = current_question + 1

    poll_len = state_data['poll_len']
    poll_len -= 1 if survey_type == 'new' else 0
    if next_question < poll_len:
        question, options = poll_questions[next_question]
        if len(options) < 1:
            await state.set_state(FeedbackState.get_other_option)
            await state.update_data({'question_for_another_option': question, 'current_question': next_question})
            await message.answer(text=f'{question}\n\nWrite your detailed answer')
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"poll_answer:{next_question}:{idx}")] for idx, option in
            enumerate(options)
        ])
        await message.answer(text=question, reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Menu', callback_data='menu')]
        ])

        text = await write_poll_results(survey_type, tg_user_service, feedback_service, message.from_user.id, results)
        await state.clear()
        await message.answer(text=text, reply_markup=keyboard)
