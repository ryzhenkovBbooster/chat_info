from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter, LEFT
from sqlalchemy import select, ScalarResult
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ContentType, ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.filters.chat_update import AddOrUpdateChatFilter
from src.service.admin.redis_service import clear_cache_not_chat_cache
from src.service.bot_updates.chat import add_chat, left_chat, update_to_supergroup
from src.db.models import Auth
from structure.misc import redis

router = Router()




@router.message(AddOrUpdateChatFilter())
async def bot_added(message: Message, session: AsyncSession):
    if message.migrate_from_chat_id or message.migrate_to_chat_id:
        print(message.chat.id, 'message')

        old_chat_id = message.migrate_from_chat_id or message.migrate_to_chat_id
        new_chat_id = message.chat.id
        update = await update_to_supergroup(session, int(old_chat_id), int(new_chat_id))
        if update == False:
            pass
        else:
            cache = await redis.get(str(old_chat_id) + 'info')
            if cache is not None:
                await redis.rename(str(old_chat_id) + 'info', str(new_chat_id) + 'info')
                await clear_cache_not_chat_cache()



    chat_id = message.chat.id
    chatname = message.chat.full_name
    await add_chat(session, chat_id=chat_id, chatname=chatname)




@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> LEFT))
async def bot_deleted(event: ChatMemberUpdated, session: AsyncSession):
    chat_id = event.chat.id
    await left_chat(session, chat_id)