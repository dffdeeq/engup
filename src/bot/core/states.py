from aiogram.fsm.state import State, StatesGroup


class SpeakingState(StatesGroup):
    first_part = State()
    second_part = State()
    third_part = State()


class WritingState(StatesGroup):
    get_user_answer = State()
