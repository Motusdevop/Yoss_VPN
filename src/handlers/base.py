from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import settings
from keyboards import Contact, Menu, Choose_Instruction, ServerKeyboard, BuyOrExtend
from texts import instructions_for_PC, instructions_for_phone

from forms.register import RegisterForm
from forms.vpn import BuyVPN, MyVPN
from repository import UserRepository, TariffRepository, SubscriptionRepository, ConfigRepository, ServerRepository

router = Router()


def get_tariff_text(id: int):
    tariff = TariffRepository.get(1)
    text = f'Вы выбрали {tariff.name} за {tariff.price} рублей\n'
    text += f'Переведите {tariff.price} рублей на `{settings.phone_number}` по СБП\n'
    text += f'После оплаты нажмите кнопку "Проверить Оплату"\n\n'
    text += f'После потверждения оплаты, вам отправят файл конфигурации для VPN'

    return text


async def check_register(message: Message, state: FSMContext):
    if not UserRepository.check_registration(message.chat.id):
        await message.answer(
            'Пожалуйста сначала зарегистрируйтесь. Для этого нажмите кнопку: "Отправить свой контакт ☎️"',
            reply_markup=Contact.markup)
        await state.set_state(RegisterForm.phone)
        return False
    return True


@router.message(F.text, Command('start'))
async def start(message: Message, state: FSMContext):
    await message.answer('Привет! Если хочешь начать пользоваться хорошим VPN за адекватные деньги, то ты по адресу',
                         reply_markup=Menu.markup)

    await check_register(message, state)

@router.message(F.text, Command('help'))
async def help(message: Message, state: FSMContext):
    await message.answer('Для помощи обращайтесь к администратору @Kapchonka77', reply_markup=Menu.markup)

@router.message(F.text.lower() == 'инструкция по активации')
async def instruction(message: Message, state: FSMContext):
    await message.answer('Для какой плотформы?', reply_markup=Choose_Instruction.markup)


@router.message(F.text.lower() == 'windows/macos/linux')
async def PC(message: Message, state: FSMContext):
    await message.answer(instructions_for_PC, reply_markup=Menu.markup)


@router.message(F.text.lower() == 'android/ios')
async def phone(message: Message, state: FSMContext):
    await message.answer(instructions_for_phone, reply_markup=Menu.markup)


@router.message(F.text.lower() == 'купить/продлить vpn')
async def buy_vpn(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)
        subscriptions_list = SubscriptionRepository.get_from_user_id(user.id)
        if len(subscriptions_list) == 0:
            server_keyboard = ServerKeyboard()
            await state.set_state(BuyVPN.server_id)
            await message.answer('Выберите интересующуй вас сервер', reply_markup=server_keyboard.markup)
        else:
            await state.set_state(BuyVPN.buy_or_extend)
            await message.answer('Выберите действие', reply_markup=BuyOrExtend.markup)


@router.message(F.text.lower() == 'мой vpn')
async def my_vpn(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get_from_chat_id(message.from_user.id)

        subscriptions_list = SubscriptionRepository.get_from_user_id(user.id)

        if not len(subscriptions_list) == 0:
            kb = []

            for subscription in subscriptions_list:
                config = ConfigRepository.get(subscription.config_id)
                server = ServerRepository.get(config.server_id)

                kb.append([InlineKeyboardButton(text=f'{server.country} [{server.id}] закончится: {subscription.expires_on.strftime("%d.%m.%Y")}',
                                                callback_data=f'{subscription.id}')])

            kb.append([InlineKeyboardButton(text='Отмена', callback_data='cancel')])

            markup = InlineKeyboardMarkup(inline_keyboard=kb)

            await state.set_state(MyVPN.subscription_id)
            await message.answer('Выберите одну из ваших подписок:', reply_markup=markup)

        else:
            await message.answer('У вас пока нет подписок.', reply_markup=Menu.markup)


