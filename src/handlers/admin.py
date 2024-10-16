from datetime import datetime, timedelta
from typing import List

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import settings
from exceptions import UserNotFoundException
from models import Server, Transaction, Config, Subscription

from repository import UserRepository, ServerRepository, TransactionRepository, TariffRepository, ConfigRepository, \
    SubscriptionRepository
from handlers.base import check_register
from forms.admin import CheckPay, UserManager, SubscriptionManager

from tools import api, vpn, bot_mode

from keyboards import UserManagementKeyboard, SubscriptionKeyboard

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

@router.message(Command('user_manage'))
async def user_manage(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            UserRepository.get_all()
            for user in UserRepository.get_all():
                await message.answer(f'id={user.id}\nusername={user.username}\nrole={user.role}')
        else:
            await message.answer('Вы не администратор')

@router.message(Command('user'))
async def user(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            args = message.text.split()
            try:
                id = int(args[1])
                user = UserRepository.get(id)
                await message.answer(f'id={user.id}\nusername={user.username}\nrole={user.role}', reply_markup=UserManagementKeyboard.markup)
                await state.update_data(user=user)
                await state.set_state(UserManager.action)
            except ValueError:
                await message.answer('Комманда введена некорректно')
        else:
            await message.answer('Комманда введена некорректно')


@router.callback_query(UserManager.action)
async def user_manage(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data == 'delete':
        data = await state.get_data()

        user = data['user']

        transaction_list = TransactionRepository.get_from_user_id(user.id)
        for transaction in transaction_list:
            TransactionRepository.delete(transaction.id)

        subscription_list = SubscriptionRepository.get_from_user_id(user.id)
        for subscription in subscription_list:
            config = ConfigRepository.get(subscription.config_id)
            server = ServerRepository.get(config.server_id)

            ip_address = f'http://{server.address}:{server.port}'
            ConfigRepository.delete(config.id)
            ServerRepository.update(server.id, count_of_configs=server.count_of_configs-1)

            api.delete_config(ip_address, config.name)
            SubscriptionRepository.delete(subscription.id)


        UserRepository.delete(user.id)

        await callback.message.answer('Пользователь удален')
    elif callback.data == 'subscriptions':
        data = await state.get_data()
        user = data['user']
        subscription_list = SubscriptionRepository.get_from_user_id(user.id)

        for subscription in subscription_list:
            text = f'''id={subscription.id}
config_id={subscription.config_id}
created_on={subscription.created_on}
expires_on={subscription.expires_on}
user_id={subscription.user_id}
'''
            await callback.message.answer(text)

@router.message(Command('subscription'))
async def subscription_manager(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        if user.role == 'admin':
            args = message.text.split()
            try:
                id = int(args[1])

                subscription = SubscriptionRepository.get(id)

                text = f'''id={subscription.id}
config_id={subscription.config_id}
created_on={subscription.created_on}
expires_on={subscription.expires_on}
user_id={subscription.user_id}
'''
                await message.answer(text, reply_markup=SubscriptionKeyboard.markup)
                await state.update_data(subscription=subscription)
                await state.set_state(SubscriptionManager.action)
            except ValueError:
                await message.answer('Комманда введена некорректно')

@router.callback_query(SubscriptionManager.action)
async def subscription_manager(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    subscription = data['subscription']
    if callback.data == 'delete':

        SubscriptionRepository.delete(subscription.id)
        await callback.message.answer('Подписка удалена')

    elif callback.data == 'delete_config':

        SubscriptionRepository.delete(subscription.id)

        config = ConfigRepository.get(subscription.config_id)

        server = ServerRepository.get(config.server_id)

        ip_address = f'http://{server.address}:{server.port}'

        ConfigRepository.delete(subscription.config_id)

        api.delete_config(ip_address, config.name)
        ServerRepository.update(server.id, count_of_configs=server.count_of_configs - 1)

        await callback.message.answer('Подписка и конфиг удалены')

    elif callback.data == 'change_expire':

        await callback.message.answer('Введите новый срок ex: 30.12.2006')
        await state.update_data(subscription=subscription)
        await state.set_state(SubscriptionManager.expire)

@router.message(SubscriptionManager.expire)
async def expire_change(message: Message, state: FSMContext):
    data = await state.get_data()
    subscription = data['subscription']

    date = datetime.strptime(message.text, '%d.%m.%Y')

    SubscriptionRepository.set_expired_on(subscription.id, date)

    await message.answer('Подписка обновлена')



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

# @router.message(Command('server'))
# async def server(message: Message, state: FSMContext):
#     if await check_register(message, state):
#         user = UserRepository.get_from_chat_id(message.from_user.id)
#         if user.role == 'admin':
#             try:
#                 args = message.text.split()
#                 id = int(args[1])
#                 server = ServerRepository.get(id)
#                 await state.update_data(server=server)
#
#                 text = f'''Сервер {id}, адрес: {server.address}:{server.port},
# кол-во конфигов: {server.count_of_configs}'''
#                 await message.answer(text, reply_markup=ServerManageKeyboard.markup)


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

                await callback.message.delete()
                await state.clear()

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
