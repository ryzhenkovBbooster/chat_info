from datetime import datetime

from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import sessionmaker
from src.filters.check_updates import CheckUpdatesChat
from src.service.chat_info.chat_info_service import appent_info_in_bd, check_memory_and_date
from structure.misc import redis

router = Router()

@router.message(CheckUpdatesChat(session_pool=sessionmaker))
async def get_message(message: Message, session: AsyncSession):
    text = message.text

    if text is not None:
        text = message.from_user.full_name + '\n' + text +';\n'
        chat_id = message.chat.id


        # today_cache_data = today_cache_data.replace(minute=0, second=0, microsecond=0, hour=0)

        await check_memory_and_date(message=message, text=str(text), session=session, chat_id=int(chat_id))

        # cache = await redis.get(name=str(chat_id) + 'chat')
        # await message.answer(f'{cache.decode("utf-8")}')




