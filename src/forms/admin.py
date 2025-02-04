from aiogram.fsm.state import State, StatesGroup


class CheckPay(StatesGroup):
    confirm = State()


class UserManager(StatesGroup):
    action = State()


class SubscriptionManager(StatesGroup):
    action = State()
    expire = State()


# class ServerManager(StatesGroup):
#     action = State()
#     count_of_configs = State()
