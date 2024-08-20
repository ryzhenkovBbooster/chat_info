from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select, ScalarResult, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Auth
from structure.misc import redis

## машина состояния для выдачи доступа к боту
class Add_access(StatesGroup):
    get_user = State()
    edit_access = State()


## получаем всех пользователей в боте

async def users_service(session: AsyncSession):
    arr = []
    result = await session.execute(select(Auth))
    result: ScalarResult
    users: Auth = result.all()
    for user in users:
        user: Auth
        arr.append({
            "username": user[0].username,
            "user_id": user[0].user_id,
            "access": 'admin' if user[0].access else 'client'})

    return  arr

## меняем уровень доступа к боту
async def edit_access_service(session: AsyncSession, user, user_info, user_id):

    if user_info == 'admin':
        user_info = False
    else:
        user_info = True
    await session.execute(update(Auth).where(Auth.username == user).values(access=user_info))
    await session.commit()
    await redis.set(name=user_id, value='1' if user_info else '0')

# async def add_june_indb(session: AsyncSession, username: str):
#     data = await redis.get(name='user_id')
#     if data is None:
#         data = await session.execute(select(Auth).where(Auth.username==username))
#         data: ScalarResult
#         user: Auth = data.one_or_none()
#         if user is not None:
#             return True
#         else:
#             try:
#
#                 course_june = Auth(
#                     username=username,
#                     access=False
#
#                 )
#                 await session.merge(course_june)
#                 await session.commit()
#                 return True
#             except IntegrityError:
#                 return False
#
#     else:
#         return True









# async def about_user_service(session: AsyncSession, username: str):
#     result = await session.execute(select(Auth).where(Auth.username == username))
#     result: ScalarResult
#
#     user: Auth = result.one_or_none()
#     if user is None:
#         return None
#     elif user[0].access == False:
#         return 'client'
#     else:
#         return 'admin'