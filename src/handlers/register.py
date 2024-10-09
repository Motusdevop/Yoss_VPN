from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import Menu
from forms.register import RegisterForm
from models import User

from repository import UserRepository

router = Router()

@router.message(RegisterForm.phone)
async def register(message: Message, state: FSMContext):
    contact = message.contact

    if contact:

        nickname = contact.first_name + ' ' + contact.last_name if contact.last_name else contact.first_name
        username = message.from_user.username
        chat_id = contact.user_id
        phone = contact.phone_number

        user = User(nickname=nickname, username=username, chat_id=chat_id, phone=phone)
        UserRepository.add(user)

        # UserRepository.register_user(fullname=fullname, username=username, telegram_id=telegram_id, phone=phone)
        await message.answer(f'Вы успешно зарегистровались, спасибо ✅', reply_markup=Menu.markup)

    await state.clear()