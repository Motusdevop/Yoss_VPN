import asyncio
from datetime import datetime

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile

from forms.vpn import MyVPN, BuyVPN
from repository import SubscriptionRepository, ConfigRepository, ServerRepository, UserRepository

from keyboards import MyVPNKeyboard, TariffKeyboard

from tools import api

router = Router()

@router.callback_query(MyVPN.subscription_id)
async def send_subscription(callback: CallbackQuery, state: FSMContext):
    if callback.data != 'cancel':
        subscription_id = int(callback.data)

        subscription = SubscriptionRepository.get(subscription_id)
        config_id = subscription.config_id
        config = ConfigRepository.get(config_id)
        server_id = config.server_id
        server = ServerRepository.get(server_id)

        ip_adress = f'http://{server.address}:{server.port}'

        text = f"""
<b>Подписка до {subscription.expires_on.strftime('%d.%m.%Y')}</b>
<b>Страна: {server.country} [{server.id}]</b>
<b>Сервер: {'🟢 работает' if api.ping(ip_adress) else '🔴 не работает'}</b>
<b>Конфиг: {'🟢 работает' if not config.disabled else '🔴 не работает'}</b>
<b>Имя конфига: {config.name}</b>

<b>Выберите действие:</b>
"""
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=MyVPNKeyboard.markup, parse_mode=ParseMode.HTML)
        await state.update_data(subscription_id=subscription_id)
        await state.set_state(MyVPN.action)


    else:
        await callback.message.delete()
        await state.clear()

@router.callback_query(MyVPN.action)
async def action(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    if callback.data != 'cancel':
        if callback.data == 'extend':
            tariff_keyboard = TariffKeyboard(UserRepository.get_from_chat_id(callback.from_user.id), extend=True)

            await state.set_state(BuyVPN.tariff)
            await callback.message.answer('Выберите на сколько вы хотите продлить',
                                          reply_markup=tariff_keyboard.markup)

        if callback.data == 'recreate':
            data = await state.get_data()

            subscription = SubscriptionRepository.get(int(data['subscription_id']))

            if datetime.now() > subscription.expires_on:
                await state.clear()
                await callback.message.answer('Ваша подписка больше не действует, сначала продлите её')

            else:
                msg = await callback.message.answer('Ожидайте...')

                config_id = subscription.config_id
                config = ConfigRepository.get(subscription.config_id)

                server_id = config.server_id
                server = ServerRepository.get(server_id)

                ip_address = f'http://{server.address}:{server.port}'

                if api.ping(ip_address):

                    api.delete_config(config_name=config.name, ip_address=ip_address)
                    await asyncio.sleep(1)
                    result = api.create_config(config_name=config.name, ip_address=ip_address)

                    file = result[config.name]

                    ConfigRepository.update(config_id, file=file)
                    await msg.delete()

                    await callback.message.answer('Конфиг пересоздан:')
                    await callback.message.answer(f'```{file}```', parse_mode=ParseMode.MARKDOWN)
                    await callback.message.answer_photo(api.generate_qr(file))

                else:
                    await msg.delete()
                    await state.clear()
                    await callback.message.answer('Не удалось подключиться к серверу, попробуйте позже')

        if callback.data == 'get_config':
            data = await state.get_data()

            subscription = SubscriptionRepository.get(int(data['subscription_id']))
            config = ConfigRepository.get(subscription.config_id)

            await callback.message.answer('Конфиг:')
            file = BufferedInputFile(str.encode(config.file), 'YossVPN.conf')
            await callback.message.answer_document(file)

            await callback.message.answer_photo(api.generate_qr(config.file))
    else:
        await state.clear()

