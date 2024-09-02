from datetime import datetime

from aiogram.types import Message
from sqlalchemy import update, func, text, String, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ChatInfo
from structure.misc import redis


async def check_memory_and_date(message: Message, text: str, session: AsyncSession, chat_id: int):
    cache_chat_data = await redis.get(name=str(chat_id) + 'info')
    if not cache_chat_data:
        await redis.set(name=str(chat_id) + 'info', value=str(text) + '\n')
        return
    cache_chat_data = cache_chat_data.decode('utf-8')
    if len(cache_chat_data) >= 1000:
        await redis.append(str(message.chat.id) + 'info', str(text) + '\n')
        await appent_info_in_bd(session=session, textx=cache_chat_data, chat_id=chat_id)
        await redis.delete(str(chat_id) + 'info')

    else:
        await redis.append(str(message.chat.id) + 'info', str(text) + '\n')





    # memory_usage: int = await redis.memory_usage(str(message.chat.id) + 'info')
    # max_range = 31457280
    # if memory_usage is None:
    #     memory_usage = 0


    # today_date = datetime.today().date()
    # today_cache_data: str or None = await redis.get(name=str(message.chat.id) + 'time')
    # if today_cache_data is not None:
    #
    #     today_cache_data = today_cache_data.decode('utf-8')

    # if not today_cache_data:
    #     await redis.set(name=str(message.chat.id) + 'time', value=today_date.strftime('%Y-%m-%d'))
    #     today_cache_data = today_date.strftime('%Y-%m-%d')

    # today_cache_data = datetime.strptime(today_cache_data, '%Y-%m-%d').date()
    #
    # # today_cache_data = today_cache_data.replace(minute=0, second=0, microsecond=0, hour=0)
    #
    # if today_date > today_cache_data or memory_usage >= max_range:
    #     # print('сработало условие')
    #     # print(today_date, type(today_date), 'today_date')
    #     # print(today_cache_data, type(today_cache_data), 'today_cache_data')
    #
    #     # await redis.set(name=str(message.chat.id) + 'time', value=str(datetime.today()))
    #
    #     cache_chat_data = cache_chat_data.decode('utf-8')
    #     await appent_info_in_bd(session=session, textx=cache_chat_data, chat_id=chat_id)
    #     await redis.delete(str(chat_id) + 'info')
    #
    #
    # else:
    #     await redis.append(str(message.chat.id) + 'info', str(text) + '\n')


async def appent_info_in_bd(session: AsyncSession, textx: str, chat_id: int):
    try:


        await session.execute(
            text(f"UPDATE public.chat_info SET messages = CONCAT(messages, :new_message) WHERE chat = :chat_id")
            .bindparams(bindparam('new_message', type_=String)), {'new_message': textx, 'chat_id': chat_id}
        )
        # await session.execute(update(ChatInfo).where(ChatInfo.chat == int(chat_id)).values(messages=func.concat(ChatInfo.messages, str(text))))
        await session.commit()
        return True
    except Exception as e:
        print(e)
        return False