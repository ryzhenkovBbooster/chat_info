
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, ScalarResult, update, values

from src.db.models import Chat




## функция которая добавляет в бд имя чата и id при добавлении бота в чат
async def add_chat(session: AsyncSession, chat_id: int, chatname: str):
    result = await session.execute(select(Chat).where(chat_id == Chat.chat_id ))
    result: ScalarResult

    chat: Chat = result.one_or_none()
    if chat is not None:
        await session.execute(update(Chat).where(chat_id == Chat.chat_id).values(add_or_left=True))
        return False
    else:
        chat = Chat(
            chatname=chatname,
            chat_id=chat_id,



        )
        await session.merge(chat)
        await session.commit()

        return True

## функция которая меняет значение в бд когда бота кикают из чата

async def left_chat(session: AsyncSession, chat_id: int):
    await session.execute(update(Chat).where(Chat.chat_id == chat_id).values(add_or_left=False))
    await session.commit()



async def update_to_supergroup(session: AsyncSession, old_chat_id: int, new_chat_id: int):
    try:

        result = await session.execute(update(Chat).where(Chat.chat_id == old_chat_id).values(chat_id=new_chat_id))
        await session.commit()
        if result != 0:

            return True
        return False
    except:
        return False