import datetime
import json

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from src.FSM.work_with_chats import Chat_work, Delete_access_services
from src.db.database import sessionmaker
from src.db.models import ChatInfo

from src.filters.guard import UserAccessFilter
from src.keyboards.for_admin import get_all_from_chat_key, get_active_or_unactive_chats, crud_premission, get_chat_key, \
    cancel_key, restart_add_course_june_key, close_chat
from src.filters.private_chat import PrivateChat
from src.service.admin.chats import get_groups_service, get_active_unactiv_groups_service, \
    get_one_chat_service, get_info_about_active_chat, pull_init_chat, chat_closed_service

# from src.service.admin.course_june import attach_user_from_chat_service, create_email_service, \
#     create_practical_task_service, check_manager_in_bot, create_personnel_folder_service, check_start_service_in_kn, \
#     attach_user_from_course, get_email_june_service, create_june
# from src.service.admin.init_course import get_init_data
# from src.service.admin.takeback_accesses_from_june import get_accesses_service, remove_access_service

from structure.misc import redis


router = Router()


### функция отмены действия
@router.callback_query(Chat_work.get_chats, F.data == 'back_to_menu')
@router.callback_query(Chat_work.get_chats_active_or_unactive, F.data == 'back_to_menu')
@router.callback_query(Chat_work.get_chat, F.data == 'back_to_menu')
@router.callback_query(Chat_work.get_active_chat, F.data == 'back_to_menu')
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('back to menu', reply_markup=crud_premission())


## функция получение всех чатов
@router.message(F.text.lower() == "chats", UserAccessFilter(session_pool=sessionmaker), PrivateChat())
async def get_all_chats(message: Message, session: AsyncSession, state: FSMContext):
    chats = await get_groups_service(session)
    await message.answer(text=f'Выбирите категорию',
                         reply_markup=get_active_or_unactive_chats(chats=chats))


    await state.set_state(Chat_work.get_chats)


## функция получение активных чатов
@router.callback_query(
    Chat_work.get_chats,
    F.data.func(lambda data: json.loads(data)['data']) == True,
    F.data.func(lambda data: json.loads(data)['archiv']) == False
)
async def get_active_chats(callback: CallbackQuery, session: AsyncSession, state: FSMContext):

    chats = await get_active_unactiv_groups_service(session, True, archiv=False)
    await callback.message.answer(text='активные чаты', reply_markup=get_all_from_chat_key(chats))
    await state.set_state(Chat_work.get_active_chat)


## функция получение не активных чатов
@router.callback_query(
    Chat_work.get_chats,
    F.data.func(lambda data: json.loads(data)['data']) == False,
    F.data.func(lambda data: json.loads(data)['archiv']) == False
)
async def get_unactive_chats(callback: CallbackQuery, session: AsyncSession, state: FSMContext):

    chats = await get_active_unactiv_groups_service(session, False, archiv=False)
    await callback.message.answer(text='не активные чаты', reply_markup=get_all_from_chat_key(chats))
    await state.set_state(Chat_work.get_chat)


@router.callback_query(Chat_work.get_chats, F.data.func(lambda data: json.loads(data)['archiv']) == True)
async def get_archiv_chats(callback: CallbackQuery, session: AsyncSession, state: FSMContext):

    chats = await get_active_unactiv_groups_service(session, False, True)
    await callback.message.answer(text='архив', reply_markup=get_all_from_chat_key(chats))
    await state.set_state(Chat_work.archiv)

@router.callback_query(Chat_work.archiv)
async def get_archiv_chat(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    chat = callback.data
    await state.clear()
    if chat is None:
        await callback.message.answer('err: чат не найден в базе данных')

    else:
        pull: ChatInfo = await get_info_about_active_chat( session, chat_id=int(chat))
        if pull is False or (type(pull) == tuple and pull[0] == False):
            await callback.message.answer(f'Ошибка при запросе в бд\nstate: get_active_chat\nerr: {str(pull)}')
        else:
            resident_id = pull.resident_id
            await callback.message.answer(f'chat_id: {chat}\nresident: {resident_id}', reply_markup=crud_premission())


            #

#




@router.callback_query(Chat_work.get_active_chat)
async def get_one_active_chat(callback: CallbackQuery, state: FSMContext, session: AsyncSession):


    chat = callback.data
    await state.clear()

    if chat is None:
        await callback.message.answer('err: чат не найден в базе данных')

    else:
        pull: ChatInfo = await get_info_about_active_chat( session, chat_id=int(chat))
        if pull is False or (type(pull) == tuple and pull[0] == False):
            await callback.message.answer(f'Ошибка при запросе в бд\nstate: get_active_chat\nerr: {str(pull)}')
        else:
            resident_id = pull.resident_id


            await callback.message.answer(f'chat_id: {chat}\nresident: {resident_id}', reply_markup=close_chat(int(chat)))


            #
            await state.set_state(Delete_access_services.select_access)

@router.callback_query(Delete_access_services.select_access)
async def chat_closed(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    chat_id = int(callback.data)
    pull = await chat_closed_service(session, chat_id)
    if pull is True:
        await callback.message.answer(' Чат перенесен в архив', reply_markup=crud_premission())

    else:
        await callback.message.answer(f'ошибка при обновлении записи в бд\nstate: chat_closed\nchat_id: {chat_id}\nerr: {str(pull)}')


# @router.message(F.text.lower() == 'забрать доступы', Delete_access_services.select_access)
# async def select_access_services(message: Message, session: AsyncSession, state: FSMContext):
#     data = await state.get_data()
#     chat_id = data['chat_id']
#     results = await remove_access_service(session, chat_id)
#     title = await message.bot.get_chat(chat_id=chat_id)
#     title = title.title
#     if results:
#         await message.bot.set_chat_title(chat_id=chat_id, title='Архив ' + str(title))
#         response_text = '\n'.join(
#             f"{func_name} returned {'True' if result else 'False'}" for func_name, result in results.items())
#         await message.answer(text=response_text)
#     else:
#         await message.answer(text='false')
#     await state.clear()


## функция получение одного чата из выборки активных\неактивных чатов
@router.callback_query(Chat_work.get_chat)
async def get_one_chat(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == 'cancel':
        data = await state.get_data()
        data = data.get('get_one_chat', None)
    else:

        data = callback.data
        await state.update_data(get_one_chat=data)
    chat = await get_one_chat_service(session, data)
    if chat is not None:
        text = f"Название чата {chat['chatname']}\n ID чата {chat['chat_id']}"
        await callback.message.answer(text=text, reply_markup=get_chat_key())
        # await state.clear()
        await state.update_data(chat_id=chat['chat_id'])
        await state.set_state(Chat_work.initialization_chat)
        await state.update_data()
    else:
        await callback.message.answer('такого чата не существует')
        # await state.clear()


## функция инициализцация карточки резидента\ получение  имени пользователя телеграма новичка
@router.message(Chat_work.initialization_chat, UserAccessFilter(session_pool=sessionmaker))
@router.callback_query(Chat_work.initialization_chat, UserAccessFilter(session_pool=sessionmaker))
async def start_kn(message: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data = data.get('chat_id')
    await state.clear()
    await state.update_data(chat_id=data)
    await message.answer('введите id резидента из ГК')

    await state.set_state(Chat_work.check_info)


# @router.message(Chat_work.resident_id)
# async def input_fullname(message: Message, state: FSMContext):
#         await message.answer('введите полное имя сотрудника через пробел')
#         await state.update_data(redident_id=int(message.text))
#         await state.set_state(Chat_work.username)


## функция получения менежера




@router.message(Chat_work.check_info)
async def check_info(message: Message, state: FSMContext, session: AsyncSession):
    resident_id = int(message.text)
    await state.update_data(resident_id=int(resident_id))


    #
    await message.answer(
        f'проверьте:\nРезидент: {resident_id}',
        reply_markup=restart_add_course_june_key())
    # print('username: ', message.from_user.username)






@router.callback_query(F.data == 'cancel')
async def cancel_oper(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    data = await state.get_data()
    prev_state = data.get('prev_state')
    prev_message = data.get('prev_message')
    # print('state: ', prev_state)
    # await callback.message.answer('Операция отменена')
    await state.set_state(prev_state)
    await callback.message.answer(prev_message, reply_markup=cancel_key())


@router.callback_query(F.data == 'again')
async def refractor_data(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.set_state(Chat_work.initialization_chat)
    # await state.da
    await start_kn(callback, state)
    await callback.answer('введите id резидента из ГК')


@router.callback_query(F.data == 'completed')
async def it_true_info(callback: CallbackQuery, state: FSMContext, session: AsyncSession):

    currnet_state = await state.get_state()
    if currnet_state is None:
        return

    data_state = await state.get_data()
    chat_id = data_state.get('chat_id')
    resident_id = data_state.get('resident_id')
    await callback.message.answer(f'{resident_id}')
    print(type(resident_id))

    pull = await pull_init_chat(session, chat_id=int(chat_id), resident_id=int(resident_id))
    if pull is True:

        await state.clear()

        await callback.message.answer('Успешная инициализация!')

    else:
        await callback.message.answer(
            f'Ошибка при записи в базу данных\nstate: {callback.data}\ndata: {data_state}\nerr: {pull[1]}'
        )



@router.message(F.text.lower() == 'get cache', UserAccessFilter(session_pool=sessionmaker))
async def get_all_cache(message: Message):
    all_keys_values = {}
    while True:
        cursor, keys = await redis.scan(cursor=cursor, match='*', count=100)
        for key in keys:
            all_keys_values[key.decode('utf-8')] = await redis.get(key).decode('utf-8')
        if cursor == 0:
            break

    # Вывод всех ключей и значений
    for key, value in all_keys_values.items():
        print(f"Key: {key}, Value: {value}")

    await message.answer('success')