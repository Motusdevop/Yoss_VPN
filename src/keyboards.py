from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from models import Server, User, Tariff
from repository import ServerRepository, TariffRepository


class Menu():
    kb = [[KeyboardButton(text='Купить VPN')],
          [KeyboardButton(text='Инструкция по активации'), KeyboardButton(text='О нас')],
          [KeyboardButton(text='Мой VPN')]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class Choose_Instruction():
    kb = [[KeyboardButton(text='Windows/MacOS/Linux'), KeyboardButton(text='Android/IOS')]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class Contact():
    kb = [[KeyboardButton(text='Отправить свой контакт ☎️', request_contact=True)]]

    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

class ServerKeyboard():
    def __init__(self):
        server_list = ServerRepository.get_all()

        self.server_list: List[Server] = ServerRepository.get_all()

        self.kb = [[InlineKeyboardButton(text=server.country + f'[{server.id}]', callback_data=str(server.id))] for server in self.server_list]

        self.markup = InlineKeyboardMarkup(inline_keyboard=self.kb)

class TariffKeyboard():
    def __init__(self, user: User):

        self.kb = [[]]

        tariff_one_month = TariffRepository.get(1) # 1 месяц
        tariff_three_month = TariffRepository.get(2) # 3 месяца

        if user.free_trial:
            self.kb = [[InlineKeyboardButton(text='2 дня, Бесплатно', callback_data='free_trial')]]

        self.kb.append([InlineKeyboardButton(text=f'1 месяц, {tariff_one_month.price} рублей', callback_data='one_month')])
        self.kb.append([InlineKeyboardButton(text=f'3 месяца, {tariff_three_month.price} рублей', callback_data='three_month')])
        self.kb.append([InlineKeyboardButton(text='Отменить', callback_data='cancel')])

        self.markup = InlineKeyboardMarkup(inline_keyboard=self.kb)


