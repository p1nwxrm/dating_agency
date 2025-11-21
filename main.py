# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from storage.redis_storage import storage
from handlers import router
from middleware.role_guard import RoleGuardMiddleware
from middleware.check_username import UsernameCheckMiddleware

from utils.username_checker import check_usernames_periodically


# ---------------------------
# Ініціалізація
# ---------------------------
bot = Bot(token = BOT_TOKEN)
dp = Dispatcher(storage = storage)


# ---------------------------
# Запуск
# ---------------------------
async def main():
    logging.basicConfig(level = logging.INFO)

    dp.include_router(router)

    dp.message.middleware(RoleGuardMiddleware())
    dp.callback_query.middleware(RoleGuardMiddleware())

    dp.message.middleware(UsernameCheckMiddleware())
    dp.callback_query.middleware(UsernameCheckMiddleware())

    asyncio.create_task(check_usernames_periodically(bot))  # Запускаємо фоновий цикл перевірок ВСІХ юзернеймів
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())