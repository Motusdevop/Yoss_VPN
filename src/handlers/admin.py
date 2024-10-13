from datetime import datetime, timedelta
from typing import List

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from config import settings
from exceptions import UserNotFoundException
from models import Server, Transaction, Config, Subscription

from repository import UserRepository, ServerRepository, TransactionRepository, TariffRepository, ConfigRepository, \
    SubscriptionRepository
from handlers.base import check_register
from forms.admin import CheckPay

from tools import api, vpn, bot_mode

router = Router()


@router.message(Command('add_server'))
async def add_server(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            try:
                args = message.text.split()
                address: str = args[1].split(':')[0]
                port: int = int(args[1].split(':')[-1])
                coutry: str = args[2]

                server = Server(address=address, port=port, country=coutry)
                id: int = ServerRepository.add(server)

                await message.answer(f'Сервер успешно добавлен:\nid={id}\n{address}:{port}\nстрана={coutry}')
            except ValueError:
                await message.answer('Комманда введенна некорректно')
            except IndexError:
                await message.answer('Комманда введена некорректно')


        else:
            await message.answer('Вы не администратор')

@router.message(Command('status'))
async def status(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            mode = bot_mode.BotMode()
            await message.answer(mode.status)
    else:
        await message.answer('Вы не администратор')

@router.message(Command('buy_action'))
async def tech_work(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            mode = bot_mode.BotMode()
            if mode.buy_action:
                mode.set_buy_action(False)
            else:
                mode.set_buy_action(True)

            mode = bot_mode.BotMode()

            await message.answer(mode.status)


@router.message(Command('my_vpn_action'))
async def tech_work(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            mode = bot_mode.BotMode()
            if mode.my_vpn_action:
                mode.set_my_vpn_action(False)
            else:
                mode.set_my_vpn_action(True)

            mode = bot_mode.BotMode()

            await message.answer(mode.status)

@router.message(Command('list_servers'))
async def list_servers(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':

            servers = ServerRepository.get_all()
            result = []
            for server in servers:
                text = f'''
id: {server.id}
address:port: {server.address}:{server.port}
country: {server.country}
count_of_configs: {server.count_of_configs}
'''
                result.append(text)
            await message.answer(f'Сервера:\n{" ".join([item for item in result])}')
        else:
            await message.answer('Вы не администратор')


@router.message(Command('remove_server'))
async def remove_server(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            try:
                args = message.text.split()
                id = int(args[1])
                ServerRepository.remove(id)
                await message.answer(f'Сервер {id} успешно удален')
            except ValueError:
                await message.answer('Комманда введенна некорректно')
            except IndexError:
                await message.answer('Комманда введенна некорректно')
        else:
            await message.answer('Вы не администратор')


@router.message(Command('make_admin'))
async def make_admin(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin' or settings.admin == message.from_user.id:
            message_args = message.text.split()
            try:
                admin_chat_id = int(message_args[1])
                UserRepository.make_admin(admin_chat_id)
                await message.answer('Администратор успешно добавлен')
            except ValueError:
                await message.answer('Комманда введенна некорректно')
            except UserNotFoundException:
                await message.answer('Пользователь не найден')
        else:
            await message.answer('Вы не администратор')


@router.message(Command('check_pay'))
async def check_pay(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            transaction_list: List[Transaction] = TransactionRepository.get_all()

            if len(transaction_list) == 0:
                await message.answer('Нет транзакций')

            else:
                for transaction in transaction_list:
                    user = UserRepository.get(transaction.user_id)
                    tariff = TariffRepository.get(transaction.tariff_id)

                    text = f'ID: {transaction.id} Создана: {transaction.created_on.strftime("%d.%m.%Y %H:%M")}\n'
                    text += f'{user.username}, +{user.phone} перевёл {tariff.price} на СБП'

                    kb = [[InlineKeyboardButton(text='Принять',
                                                callback_data=f'confirm {transaction.id}'),
                           InlineKeyboardButton(text='Отмена',
                                                callback_data=f'cancel {transaction.id}')]]

                    markup = InlineKeyboardMarkup(inline_keyboard=kb)
                    await message.answer(text, reply_markup=markup)

                await state.set_state(CheckPay.confirm)
        else:
            await message.answer('Вы не администратор')


@router.callback_query(CheckPay.confirm)
async def check_pay_confirm(callback: Message, state: FSMContext):
    try:
        transaction_id = int(callback.data.split(' ')[1])
        transaction = TransactionRepository.get(transaction_id)
        user = UserRepository.get(transaction.user_id)
        tariff = TariffRepository.get(transaction.tariff_id)

        if callback.data.split()[0] == 'confirm':
            if transaction.subscription_id is None:
                server = ServerRepository.get(transaction.server_id)

                config = vpn.create_config(username=user.username, user_id=user.id, server_id=server.id)
                days = 30 if tariff.name == 'one_month' else 90
                subscription_id = vpn.create_subscription(user_id=user.id, config_id=config.id, days=days)
                subscription = SubscriptionRepository.get(subscription_id)

                text = f'''
<b>Ваш платёж принят</b>
    
<b>Ваш VPN конфиг:</b>
<b>Закончится:</b> {subscription.expires_on.strftime("%d.%m.%Y")}
<b>Сервер:</b> {server.address}
<b>Страна:</b> {server.country}
<b>Стоимость:</b> {tariff.price} рублей
    
Благодарим за доверие!
'''
                await callback.bot.send_message(user.chat_id, text, parse_mode=ParseMode.HTML)
                await callback.bot.send_message(user.chat_id,
                                                f'```\n{config.file}```',
                                                parse_mode=ParseMode.MARKDOWN_V2)
                await callback.bot.send_photo(user.chat_id, api.generate_qr(config.file),
                                              caption='Qr Code для мобильных устройств')

            else:
                subscription = SubscriptionRepository.get(transaction.subscription_id)

                add_time = timedelta(days=30) if tariff.id == 1 else timedelta(days=90)

                if subscription.expires_on > datetime.now():
                    SubscriptionRepository.set_expired_on(subscription.id, subscription.expires_on + add_time)
                else:
                    SubscriptionRepository.set_expired_on(subscription.id, datetime.now() + add_time)
                    config = ConfigRepository.get(subscription.config_id)
                    server = ServerRepository.get(config.server_id)

                    ip_address = f'http://{server.address}:{server.port}'

                    api.config_on(ip_address, config_name=config.name)

                    ConfigRepository.update(config.id, disabled=False)

                text = f'''
<b>Ваш платёж принят</b>

<b>Ваш VPN конфиг продлён:</b>
<b>Закончится:</b> {(subscription.expires_on + add_time).strftime("%d.%m.%Y")}

Благодарим за доверие!
'''

                await callback.bot.send_message(user.chat_id, text, parse_mode=ParseMode.HTML)

        elif callback.data.split()[0] == 'cancel':
            await callback.bot.send_message(user.chat_id, 'Ваш платёж недействителен, для помощи напишите @Kapchonka77')

        TransactionRepository.remove(transaction_id)

        await state.clear()
    except ValueError:
        await callback.message.answer('Что-то пошло не так')
