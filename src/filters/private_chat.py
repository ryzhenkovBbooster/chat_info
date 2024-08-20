from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message
class PrivateChat(BaseFilter):



    async def __call__(self, message: Message):

        if message.chat.type != ChatType.PRIVATE:
            return False
        else:
            return True