import json

from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, ScalarResult, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.db.models import Chat, Auth, ChatInfo
from src.keyboards.for_admin import sendOtherService, edit_active_chat_key, finaly_message_from_junior_key
from src.service.chat_info.chat_info_service import appent_info_in_bd
from structure.misc import redis


## машина состояния





## получаем все группы в который есть бот

async def get_groups_service(session: AsyncSession):
    arr = []
    result = await session.execute(select(Chat))
    result: ScalarResult
    groups: Chat = result.all()
    for chat in groups:
        chat: Chat
        arr.append(chat[0].chatname)
    return arr
## пулаем отфильтрованный список, активных или неактивных групп
async def get_active_unactiv_groups_service(session: AsyncSession, status: bool, archiv: bool):
    arr = []

    if status is False and archiv is False:

        result = await session.execute(select(Chat).where(and_(Chat.active_chat == False, Chat.archiv == False)))
        result: ScalarResult
        groups: Chat = result.all()
        for chat in groups:
            chat: Chat




            arr.append({'chatname':chat[0].chatname, 'chatid':chat[0].chat_id})

        # for chat in finaly_groups:
        #     chat[0]: Chat
        #     if chat[0].chatname in arr:
        #         arr.remove({'chatname':chat[0].chatname, 'chatid':chat[0].chat_id})
        return arr
    elif status is True and archiv is False:
        result = await session.execute(select(Chat).where(and_(Chat.active_chat == True, Chat.archiv == False)))
        result: ScalarResult
        groups: Chat = result.all()
        for chat in groups:
            chat: Chat
            arr.append({'chatname':chat[0].chatname, 'chatid':chat[0].chat_id})
        return arr
    else:
        result = await session.execute(select(Chat).where(Chat.archiv == True))
        result: ScalarResult
        groups: Chat = result.all()
        for chat in groups:
            chat: Chat
            arr.append({'chatname': chat[0].chatname, 'chatid': chat[0].chat_id})
        return arr
## получаем один, конкретный чат
async def get_one_chat_service(session: AsyncSession, chat):
    result = await session.execute(select(Chat).where(Chat.chat_id == int(chat)))
    result: ScalarResult
    chat: Chat = result.one_or_none()
    if chat is not None:
        return {
            'chatname': chat[0].chatname,
            'chat_id': chat[0].chat_id

        }
    else:
        return False

## функция для получения коректного username телеграма
# def edit_username(username: str):
#     if '@' in username:
#         return username.replace('@', '')
#     if 'https://t.me/' in username:
#         return username.replace('https://t.me/', '')
#     return username

async def pull_init_chat(session: AsyncSession, resident_id: int, chat_id: int):
    try:
        resident = ChatInfo(
            chat=int(chat_id),
            resident_id=int(resident_id)
        )
        await session.merge(resident)
        await session.commit()

        result = await session.execute(
            update(Chat).where(Chat.chat_id == int(chat_id)).values(active_chat=True))
        await session.commit()
        if result:
            return True
        else:
            return False

    except Exception as e:
        return (False, e)



async def get_info_about_active_chat(session: AsyncSession, chat_id: int):
    try:
        result = await session.execute(select(ChatInfo).where(ChatInfo.chat == int(chat_id)))
        result: ScalarResult
        chat: Chat = result.one_or_none()
        if chat is not None:
            return chat[0]
        else:
            return False
    except Exception as e:
        return (False, e)




async def chat_closed_service(session: AsyncSession, chat_id: int):
    await redis.delete(str(chat_id) + 'global')
    await redis.delete(str(chat_id) + 'filter')
    cache = await redis.get(name=str(chat_id) + 'chat')
    if cache is not None:
        cache = cache.decode('utf-8')
        await appent_info_in_bd(session=session, textx=cache, chat_id=int(chat_id))
        await redis.delete(str(chat_id) + 'chat')
    try:
        result = await session.execute(update(Chat).where(Chat.chat_id == chat_id).values(archiv=True))
        await session.commit()
        if result:
            return True
        else:
            return False
    except Exception as e:
        return  (False, e)


# async def check_user_in_chat(user_id, chat_id, message: Message) -> bool:
#     try:
#         member = await message.bot.get_chat_member(chat_id, user_id)
#         print("member: ", member)
#         if member:
#             return member
#     except Exception as err:
#         print('err', err)
#         return False


# async def get_finaly_chats_service(session: AsyncSession):
#     arr = []
#     result = await session.execute(select(Chat, CourseJune).join(Chat, Chat.chat_id == CourseJune.chat).where(CourseJune.finaly_stage == 'true'))
#
#     result: ScalarResult
#     groups: Chat = result.all()
#
#     for chat in groups:
#         arr.append({'chatname':chat[0].chatname, 'chatid': chat[0].chat_id})


    # return arr
# async def get_info_about_finaly_chat_service(callback: CallbackQuery, session: AsyncSession, chat_id: int):
#     auth_curator = aliased(Auth)
#     auth_manager = aliased(Auth)
#     auth_june = aliased(Auth)
#     result = await session.execute(
#
#         select(CourseJune, auth_june,auth_manager,auth_curator, Chat)
#         .join(auth_curator, CourseJune.curator == auth_curator.user_id)
#         .join(auth_manager, CourseJune.manager == auth_manager.user_id)
#         .join(Chat, Chat.chat_id == CourseJune.chat)
#         .join(auth_june, and_(Chat.chat_id == CourseJune.chat, Chat.user_chat_id == auth_june.user_id))
#         .where(CourseJune.chat == chat_id))
#
#     result: ScalarResult
#
#     data: CourseJune = result.one_or_none()
#     if data is None:
#
#         await callback.message.answer(text='err: ошибка при получении информации о чате из базы данных')
#     else:
#
#         course_june = data[0]
#         curator = data[3]
#         manager = data[2]
#         june = data[1]
#         chat = data[4]
#
#         course_june = {column.name: getattr(course_june, column.name)
#                      for column in course_june.__table__.columns}
#
#         manager = {column.name: getattr(manager, column.name)
#                      for column in manager.__table__.columns}
#
#         curator = {column.name: getattr(curator, column.name)
#                      for column in curator.__table__.columns}
#
#         june = {column.name: getattr(june, column.name)
#                      for column in june.__table__.columns}
#
#         chat = {column.name: getattr(chat, column.name)
#                      for column in chat.__table__.columns}
#
#         time_doctor = course_june.get('time_doctor', 'не выдан')
#         lastpass = course_june.get('lastpass', 'не выдан')
#         rang = course_june.get('rang')
#         practical_task = course_june.get('create_practical_task')
#         personal_folder = course_june.get('personal_folder_link')
#         getcourse = course_june.get('getcourse')
#         skillup = course_june.get('create_skillup')
#         check_practical_task = course_june.get('check_practical_task')
#         hr_test = course_june.get('hr_tests')
#         tests_compelted = course_june.get('test_completed')
#
#         user_folder = 'https://drive.google.com/drive/folders/' + str(course_june.get('user_folder_id'))
#         if user_folder == 'https://drive.google.com/drive/folders/None':
#             user_folder = None
#         ipo_folder = 'https://drive.google.com/drive/folders/' + str(course_june.get('ipo_folder_id'))
#         if ipo_folder == 'https://drive.google.com/drive/folders/None':
#             ipo_folder = None
#
#         await callback.message.answer(text=str(
#             f"curator: @{curator['username']}\n"
#             f"manager: @{manager['username']}\n"
#             f"chat: {chat['chatname']}\n"
#             f"newcomer: @{june['username']}\n"
#             f"email june: {course_june['create_email']}\n"
#             f"rang: {rang}\n"
#             f"Practical task: {practical_task}\n"
#             f"Personal folder: {personal_folder}\n"
#             # f"User folder: {user_folder}\n"
#             # f"Ipo folder: {ipo_folder}\n"
#             f"time doctor: {time_doctor}\n"
#             f"lastpass: {lastpass}\n"
#             f"Практические задания выданы: {check_practical_task}\n"
#             f"Getcourse выдан: {getcourse}\n"
#             f"skill-up выдан: {skillup}\n"
#             f"Тесты отправлены новичку: {hr_test}\n"
#             f"Тесты пройдены: {tests_compelted}"
#
#
#
#         ))