from aiogram.fsm.state import State, StatesGroup


class RegisterForm(StatesGroup):
    phone = State()
