import asyncio
from multiprocessing import Process

from aiogram import Bot, Dispatcher
from database import create_tables


from config import settings
from handlers.base import router as base_router
from handlers.register import router as register_router
from handlers.admin import router as admin_router
from handlers.buy_or_extend_vpn import router as buy_or_extend_vpn_router
from handlers.my_vpn import router as my_vpn_router

from database_tools import create_price
from tools import scheduler

bot = Bot(token=settings.bot_token.get_secret_value())

def worker():
    asyncio.run((scheduler.scheduler(bot)))

# Запуск бота
async def main():
    dp = Dispatcher()

    dp.include_routers(base_router, register_router, my_vpn_router,
                       admin_router, buy_or_extend_vpn_router)

    process = Process(target=worker)
    process.start()

    await bot.delete_webhook(drop_pending_updates=True)
    create_tables()
    create_price()
    await dp.start_polling(bot)

    process.join()


if __name__ == "__main__":
    asyncio.run(main())