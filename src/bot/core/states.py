from aiogram.fsm.state import State, StatesGroup


class SpeakingState(StatesGroup):
    first_part = State()
    second_part = State()
    third_part = State()


class WritingState(StatesGroup):
    get_user_answer = State()
    ending = State()


class AdminState(StatesGroup):
    get_uq_id = State()


class FeedbackState(StatesGroup):
    get_other_option = State()

    get_user_review = State()
