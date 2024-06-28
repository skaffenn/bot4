from aiogram.fsm.state import State, StatesGroup


class UsersThreadIds(StatesGroup):
    thread_id = State()
