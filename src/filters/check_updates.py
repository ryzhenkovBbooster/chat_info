from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select, ScalarResult, and_
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.db.models import ChatInfo, Chat
from structure.misc import redis


class CheckUpdatesChat(BaseFilter):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool


    async def __call__(self, message: Message):
        chat_id = str(message.chat.id)
        res = await redis.get(name=chat_id + 'global')

        if res == b"1":
            return True

        if not check_member_is_chat(message):
            return False

        if not check_private_chat(message):
            return False
        #
        if not await check_active_chat(message, self.session_pool):
            return False

        await redis.set(name=chat_id + 'global', value='1')
        return True










def check_member_is_chat(message: Message):
    if message.migrate_from_chat_id:
        return False
    if message.new_chat_members:
        for user in message.new_chat_members:
            user_id = user.id
            if user_id == message.bot.id:
                return False
    if message.left_chat_member is not None and message.left_chat_member or message.group_chat_created == True or message.supergroup_chat_created == True:

        return False

    else:
        return True


async def check_active_chat(message: Message, session_pool: async_sessionmaker):
    res = await redis.get(name=str(message.chat.id) + 'filter')
    if not res:
            async with session_pool() as session:
                async with session.begin():


                    result = await session.execute(select(Chat).where(and_(Chat.chat_id == int(message.chat.id), Chat.active_chat == True, Chat.archiv == False)))
                    result: ScalarResult

                    chat: Chat = result.one_or_none()


                    if chat is None:

                        return False


                    await redis.set(name=str(message.chat.id) + 'filter', value='1')

                    return True

    if res == b"1":
        return True


    return False
def check_private_chat(message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return True
    else:
        return False