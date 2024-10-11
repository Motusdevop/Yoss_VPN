import asyncio

from aiogram import Bot, Dispatcher
from database import create_tables


from config import settings
from handlers.base import router as base_router
from handlers.register import router as register_router
from handlers.admin import router as admin_router
from handlers.buy_or_extend_vpn import router as buy_or_extend_vpn_router

from database_tools import create_price
# Запуск бота
async def main():
    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(base_router, register_router, admin_router, buy_or_extend_vpn_router)

    await bot.delete_webhook(drop_pending_updates=True)
    create_tables()
    create_price()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())