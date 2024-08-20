from aiogram.fsm.state import StatesGroup, State


class Chat_work(StatesGroup):
    finaly_chats = State()
    get_active_chat = State()
    get_chats = State()
    get_chats_active_or_unactive = State()
    get_chat = State()
    initialization_chat = State()
    resident_id = State()
    check_info = State()
    complited = State()
    archiv = State()



class Delete_access_services(StatesGroup):
    select_access = State()