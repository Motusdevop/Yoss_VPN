from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards import Contact, Menu, Choose_Instruction, ServerKeyboard, TariffKeyboard
from texts import instructions_for_PC, instructions_for_phone

from forms.register import RegisterForm
from forms.vpn import BuyVPN
from repository import UserRepository, ServerRepository

router = Router()

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
    await message.answer('Привет! Я бот, который поможет тебе узнать, что твои друзья твои друзья',
                         reply_markup=Menu.markup)

    await check_register(message, state)

@router.message(F.text.lower() == 'инструкция по активации')
async def instruction(message: Message, state: FSMContext):
    await message.answer('Для какой плотформы?', reply_markup=Choose_Instruction.markup)

@router.message(F.text.lower() == 'windows/macos/linux')
async def PC(message: Message, state: FSMContext):
    await message.answer(instructions_for_PC, reply_markup=Menu.markup)

@router.message(F.text.lower() == 'android/ios')
async def phone(message: Message, state: FSMContext):
    await message.answer(instructions_for_phone, reply_markup=Menu.markup)

@router.message(F.text.lower() == 'купить vpn')
async def price_list(message: Message, state: FSMContext):
    if await check_register(message, state):
        server_keyboard = ServerKeyboard()
        await state.set_state(BuyVPN.server_id)
        await message.answer('Выберите интересующуй вас сервер', reply_markup=server_keyboard.markup)

@router.callback_query(BuyVPN.server_id)
async def select_server(callback: CallbackQuery, state: FSMContext):
    server = ServerRepository.get(int(callback.data))
    tariff_keyboard = TariffKeyboard(UserRepository.get(callback.from_user.id))
    await callback.message.answer(f'Вы выбрали сервер {server.country} [{server.id}], выберите срок аренды',
                                  reply_markup=tariff_keyboard.markup)
    await callback.message.delete()
    await state.clear()

@router.message(F.text.lower() == 'мой vpn')
async def my_vpn(message: Message, state: FSMContext):
    if await check_register(message, state):

        await message.answer('Ваш VPN')

