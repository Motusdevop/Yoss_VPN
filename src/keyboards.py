from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from tools import vpn, api
from models import Server, User, Tariff
from repository import ServerRepository, TariffRepository


class Menu():
    kb = [[KeyboardButton(text='Купить/продлить VPN 🌐')],
          [KeyboardButton(text='Инструкция по активации ❔'), KeyboardButton(text='О нас 📖')],
          [KeyboardButton(text='Мой VPN 📂')]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class Choose_Instruction():
    kb = [[KeyboardButton(text='Windows/MacOS/Linux'), KeyboardButton(text='Android/IOS')]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class Contact():
    kb = [[KeyboardButton(text='Отправить свой контакт ☎️', request_contact=True)]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class ServerKeyboard():
    def __init__(self):
        self.server_list: List[Server] = ServerRepository.get_all()

        if not len(self.server_list) == 0:
            self.kb = [[InlineKeyboardButton(text=server.country + f'[{server.id}] подключений: {server.count_of_configs}/20',
                                             callback_data=str(server.id))] for
                       server in self.server_list if server.count_of_configs < 20 and api.ping(f'http://{server.address}:{server.port}/')]
            self.kb.append([InlineKeyboardButton(text='Отменить', callback_data='no_servers')])
        else:
            self.kb = [[InlineKeyboardButton(text='Нет доступных серверов', callback_data='no_servers')]]

        self.markup = InlineKeyboardMarkup(inline_keyboard=self.kb)

class TariffKeyboard():
    def __init__(self, user: User, extend=False):

        self.kb = [[]]

        tariff_one_month = TariffRepository.get(1) # 1 месяц
        tariff_three_month = TariffRepository.get(2) # 3 месяца

        if user.free_trial and not extend:
            self.kb = [[InlineKeyboardButton(text='2 дня, Бесплатно', callback_data='free_trial')]]

        self.kb.append([InlineKeyboardButton(text=f'1 месяц, {tariff_one_month.price} рублей', callback_data='one_month')])
        self.kb.append([InlineKeyboardButton(text=f'3 месяца, {tariff_three_month.price} рублей', callback_data='three_month')])
        self.kb.append([InlineKeyboardButton(text='Отменить', callback_data='cancel')])

        self.markup = InlineKeyboardMarkup(inline_keyboard=self.kb)

class CheckPay():
    kb = [[InlineKeyboardButton(text='Проверить оплату', callback_data='check'), InlineKeyboardButton(text='Отменить', callback_data='cancel')]]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

class BuyOrExtend():
    kb = [[InlineKeyboardButton(text='Купить', callback_data='buy'), InlineKeyboardButton(text='Продлить', callback_data='extend')]]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

class MyVPNKeyboard():
    kb = [[InlineKeyboardButton(text='Получить конфигурацию', callback_data='get_config')],
          [InlineKeyboardButton(text='Продлить', callback_data='extend'),
           InlineKeyboardButton(text='Пересоздать конфиг', callback_data='recreate')],
          [InlineKeyboardButton(text='Отменить', callback_data='cancel')]]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

class UserManagementKeyboard():
    kb = [[InlineKeyboardButton(text='Удалить аккаунт', callback_data='delete'),
           InlineKeyboardButton(text='Подписки', callback_data='subscriptions')]]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

class SubscriptionKeyboard():
    kb = [[InlineKeyboardButton(text='Удалить', callback_data='delete'),
           InlineKeyboardButton(text='Удалить с конфигом', callback_data='delete_config')],
          [InlineKeyboardButton(text='Изменить время окончания', callback_data='change_expire')]]

    markup = InlineKeyboardMarkup(inline_keyboard=kb)

# class ServerManageKeyboard():
#     kb = [[InlineKeyboardButton(text='Изменить кол-во конфигов', callback_data='change_count_configs')],
#           InlineKeyboardButton(text='Отменить', callback_data='cancel')]
#
#     markup = InlineKeyboardMarkup(inline_keyboard=kb)


