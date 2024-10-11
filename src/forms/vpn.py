from aiogram.fsm.state import State, StatesGroup


class BuyVPN(StatesGroup):
    buy_or_extend = State()
    subscription_id = State()
    server_id = State()
    tariff = State()
    check_pay = State()
