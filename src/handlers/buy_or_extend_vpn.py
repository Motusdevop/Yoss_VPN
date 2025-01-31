from datetime import datetime, timedelta

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from forms.vpn import BuyVPN
from handlers.base import get_tariff_text
from keyboards import CheckPay, ServerKeyboard, TariffKeyboard
from models import Config, Subscription, Transaction
from repository import (
    ConfigRepository,
    ServerRepository,
    SubscriptionRepository,
    TariffRepository,
    TransactionRepository,
    UserRepository,
)
from tools import api, vpn

router = Router()


@router.callback_query(BuyVPN.buy_or_extend)
async def buy_or_extend(callback: CallbackQuery, state: FSMContext):
    if callback.data == "buy":
        server_keyboard = ServerKeyboard()
        await state.set_state(BuyVPN.server_id)
        await callback.message.delete()
        await callback.message.answer(
            "Выберите интересующуй вас сервер", reply_markup=server_keyboard.markup
        )
        # await callback.message.answer('Покупка второго конфига пока недоступна, скоро будет...')

    else:
        await callback.message.delete()
        user = UserRepository.get_from_chat_id(callback.from_user.id)
        subscriptions_list = SubscriptionRepository.get_from_user_id(user.id)

        kb = []

        for subscription in subscriptions_list:
            config = ConfigRepository.get(subscription.config_id)
            server = ServerRepository.get(config.server_id)

            text = f'{server.country} [{server.id}] Закончится {subscription.expires_on.strftime("%d.%m.%Y")}'

            kb.append(
                [InlineKeyboardButton(text=text, callback_data=str(subscription.id))]
            )

        kb.append([InlineKeyboardButton(text="Отмена", callback_data="cancel")])

        markup = InlineKeyboardMarkup(inline_keyboard=kb)

        await state.set_state(BuyVPN.subscription_id)
        await callback.message.answer(
            "Выберите конфиг для продления", reply_markup=markup
        )


@router.callback_query(BuyVPN.subscription_id)
async def select_subscription(callback: CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await callback.message.delete()
        await state.clear()
    else:
        try:
            await callback.message.delete()
            subscription_id = int(callback.data)
            await state.update_data(subscription_id=subscription_id)

            tariff_keyboard = TariffKeyboard(
                UserRepository.get_from_chat_id(callback.from_user.id), extend=True
            )

            await state.set_state(BuyVPN.tariff)
            await callback.message.answer(
                "Выберите на сколько вы хотите продлить",
                reply_markup=tariff_keyboard.markup,
            )
        except ValueError:
            await callback.message.delete()
            await state.clear()
            await callback.message.answer("Что-то пошло не так")


@router.callback_query(BuyVPN.server_id)
async def select_server(callback: CallbackQuery, state: FSMContext):
    if callback.data != "no_servers":
        server = ServerRepository.get(int(callback.data))
        tariff_keyboard = TariffKeyboard(
            UserRepository.get_from_chat_id(callback.from_user.id)
        )
        await callback.message.answer(
            f"Вы выбрали сервер {server.country} [{server.id}], выберите срок аренды",
            reply_markup=tariff_keyboard.markup,
        )
        await callback.message.delete()
        await state.update_data(server_id=server.id)
        await state.set_state(BuyVPN.tariff)
    else:
        await state.clear()
        await callback.message.delete()


@router.callback_query(BuyVPN.tariff)
async def select_tariff(callback: CallbackQuery, state: FSMContext):
    if callback.data != "cancel":
        if callback.data == "free_trial":
            data = await state.get_data()
            server_id = data["server_id"]

            user = UserRepository.get_from_chat_id(callback.from_user.id)
            server = ServerRepository.get(server_id)

            config = vpn.create_config(
                username=user.username, user_id=user.id, server_id=server_id
            )
            subscription_id = vpn.create_subscription(
                user_id=user.id, config_id=config.id, days=2
            )

            subscription = SubscriptionRepository.get(subscription_id)

            text = f"""
<b>Ваш VPN конфиг:</b>
<b>Закончится:</b> {subscription.expires_on.strftime("%d.%m.%Y")}
<b>Сервер:</b> {server.address}
<b>Страна:</b> {server.country}
Благодарим за доверие!
                """
            UserRepository.update(user.id, free_trial=False)

            await callback.bot.send_message(
                user.chat_id, text, parse_mode=ParseMode.HTML
            )
            await callback.bot.send_message(
                user.chat_id, f"```\n{config.file}```", parse_mode=ParseMode.MARKDOWN_V2
            )
            await callback.bot.send_photo(
                user.chat_id,
                api.generate_qr(config.file),
                caption="Qr Code для мобильных устройств",
            )
        else:
            await callback.message.delete()
            await state.update_data(tariff=callback.data)
            if callback.data == "one_month":

                text = get_tariff_text(1)

                await state.set_state(BuyVPN.check_pay)

                await callback.message.answer(
                    text, reply_markup=CheckPay.markup, parse_mode=ParseMode.MARKDOWN
                )
            elif callback.data == "three_month":

                text = get_tariff_text(2)

                await state.set_state(BuyVPN.check_pay)

                await callback.message.answer(
                    text, reply_markup=CheckPay.markup, parse_mode=ParseMode.MARKDOWN
                )

            else:
                await state.clear()
                await callback.message.answer("Что-то пошло не так")
    else:
        await state.clear()
        await callback.message.delete()


@router.callback_query(BuyVPN.check_pay)
async def check_pay(callback: CallbackQuery, state: FSMContext):
    if callback.data == "check":
        user = UserRepository.get_from_chat_id(callback.from_user.id)
        data = await state.get_data()
        if data["tariff"] == "one_month":
            tariff = TariffRepository.get(1)
        else:
            tariff = TariffRepository.get(2)

        admins = UserRepository.get_admins()

        if "subscription_id" in data.keys():
            subscription_id = int(data["subscription_id"])

            subscription = SubscriptionRepository.get(subscription_id)
            config = ConfigRepository.get(subscription.config_id)
            server_id = config.server_id

            transaction = Transaction(
                user_id=user.id,
                server_id=server_id,
                tariff_id=tariff.id,
                subscription_id=subscription_id,
            )
        else:
            transaction = Transaction(
                user_id=user.id, server_id=data["server_id"], tariff_id=tariff.id
            )

        TransactionRepository.add(transaction)

        for admin in admins:
            text = f"Проверь @{user.username} +{user.phone} на оплату по СБП на сумму {tariff.price}"
            await callback.bot.send_message(admin.chat_id, text)

        await state.clear()
        await callback.message.delete()
        await callback.message.answer("Спасибо, ожидайте потверждения оплаты")
    else:
        await callback.message.delete()
