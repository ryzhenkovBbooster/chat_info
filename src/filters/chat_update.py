from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message

class AddOrUpdateChatFilter(BaseFilter):



    async def __call__(self, message: Message):

        if message.migrate_from_chat_id or message.migrate_to_chat_id:
            return True
        if message.new_chat_members:
            for user in message.new_chat_members:
                user_id = user.id
                if user_id == message.bot.id:
                    return True


        else:
            return False