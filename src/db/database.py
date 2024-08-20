import asyncio

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from urllib.parse import quote


password = ";b;f4522"
encoded_password = quote(password)

DATABASE_URL = f"postgresql+asyncpg://postgres:{encoded_password}@postgres:5432/postgres"



Base = declarative_base()

meta = MetaData()
engine = create_async_engine(url=DATABASE_URL, echo=True, pool_pre_ping=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def db_init():
    from src.db import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)