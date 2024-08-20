from typing import Callable, Dict, Any, Awaitable
from sqlalchemy import select, ScalarResult, update
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models import Auth
from structure.misc import redis

## мидлварь проверяет пользователя на налицие информации в бд о нем, если нет то записываем, если да, то ничего не происходит
class RegisterCheck(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,

        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable],
        event:TelegramObject ,
        data: Dict[str, Any]
        ) -> Any:
        res = await redis.get(name=str(event.from_user.id))
        if not res:

        # session_maker: sessionmaker = data['sessionmaker']
            async with self.session_pool() as session:
                async with session.begin():


                    result = await session.execute(select(Auth).where(Auth.user_id == event.from_user.id))
                    result: ScalarResult

                    user: Auth = result.one_or_none()
                    if user is not None:
                        pass
                    else:
                        result = await session.execute(select(Auth).where(Auth.username == event.from_user.username))
                        result: ScalarResult

                        user: Auth = result.one_or_none()
                        if user is not None:

                            await session.execute(update(Auth).where(Auth.username == event.from_user.username)
                                                  .values(user_id=event.from_user.id))
                            await session.commit()
                        else:

                            await redis.set(name=event.from_user.id,value=1)

                            user = Auth(
                                user_id=event.from_user.id,
                                username=event.from_user.username,
                                access=False
                            )
                            await session.merge(user)
                            await session.commit()
                            await event.answer(f"Пользователь с логином {event.from_user.username} авторизован")
            return await handler(event,data)
        return await handler(event,data)