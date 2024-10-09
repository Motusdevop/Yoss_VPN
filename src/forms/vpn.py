from aiogram.fsm.state import State, StatesGroup


class BuyVPN(StatesGroup):
    server_id = State()
    tariff = State()
