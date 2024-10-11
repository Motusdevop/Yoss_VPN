from aiogram.fsm.state import StatesGroup, State


class CheckPay(StatesGroup):
    confirm = State()