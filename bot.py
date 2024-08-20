import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from dotenv import load_dotenv

from src.db.database import db_init, sessionmaker
from src.handlers import check_messages, auth
from src.handlers.admin import access, chat
from src.middlewares.db import DbSessionMiddleware
from src.middlewares.register_check import RegisterCheck
from structure.misc import redis

load_dotenv()

dp = Dispatcher(storage=RedisStorage(redis=redis))


async def on_startup():
    await db_init()
async def main() -> None:
    dp.startup.register(on_startup)
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.message.middleware(RegisterCheck(session_pool=sessionmaker))
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.include_router(auth.router)
    dp.include_routers(access.router, chat.router, check_messages.router)
    bot = Bot(os.getenv("TOKEN"))

    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())