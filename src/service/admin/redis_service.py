from sqlalchemy.ext.asyncio import AsyncSession

from src.service.chat_info.chat_info_service import appent_info_in_bd
from structure.misc import redis


async def get_all_keys():
    cursor = '0'
    keys = []
    while cursor != 0:
        cursor, partial_keys = await redis.scan(cursor=cursor)
        print('data')
        keys.extend(partial_keys)
    return keys


async def clear_cache_not_chat_cache():
    keys = await get_all_keys()
    if not keys:
        return {}
    # Преобразование байтов в строки для ключей
    keys = [key.decode('utf-8') for key in keys]
    keys_to_remove = [key for key in keys if 'info' not in key]
    if keys_to_remove:
        return await redis.delete(*keys_to_remove)


async def load_chat_cache(session: AsyncSession):
    keys = await get_all_keys()

    if not keys:
        return {}
    keys = [key.decode('utf-8') for key in keys]
    keys_to_load = [key for key in keys if 'info' in key]
    if keys_to_load:
        for i in keys_to_load:
            cache = await redis.get(i)
            chat_id = int(i.replace('info', ''))
            if cache is not None:
                cache = cache.decode('utf-8')
                await appent_info_in_bd(session=session, textx=cache, chat_id=chat_id)

        return await redis.delete(*keys_to_load)


