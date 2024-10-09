from aiogram.fsm.state import StatesGroup, State


class RegisterForm(StatesGroup):
    phone = State()