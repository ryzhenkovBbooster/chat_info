from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.db.models import Auth
from structure.misc import redis


class UserAccessFilter(BaseFilter):

    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(self, message: Message):
        res = await redis.get(name=str(message.from_user.id))

        if not res:

            async with self.session_pool() as session:
                async with session.begin():


                    result = await session.execute(select(Auth).where(Auth.user_id == message.from_user.id))
                    result: ScalarResult

                    user: Auth = result.one_or_none()


                    if user is None:
                        await message.answer('err')
                        return False

                    await redis.set(name=str(message.from_user.id), value='1' if user[0].access else '0')

                    if user[0].access == False:
                        await message.answer('Нет доступа')

                        return False
                    else:

                        return True
        if res == b"1":
            return True
        else:
            await message.answer('Нет доступа')
            await redis.delete(str(message.from_user.id))
            return False