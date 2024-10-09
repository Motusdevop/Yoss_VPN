from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import settings
from exceptions import UserNotFoundException
from models import Server

from repository import UserRepository, ServerRepository
from handlers.base import check_register

router = Router()

@router.message(Command('add_server'))
async def add_server(message: Message, state: FSMContext):

    if await check_register(message, state):
        user = UserRepository.get(message.from_user.id)
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

@router.message(Command('list_servers'))
async def list_servers(message: Message, state: FSMContext):
    if await check_register(message, state):
        user = UserRepository.get(message.from_user.id)
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
        user = UserRepository.get(message.from_user.id)
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
        user = UserRepository.get(message.from_user.id)
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



