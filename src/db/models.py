from sqlalchemy import Column, Integer, Text, BigInteger, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

from src.db.database import Base


class Auth(Base):
    __tablename__ = 'tg_auth'
    id = Column(BigInteger, unique=True, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, unique=True)
    username = Column(Text, unique=False, nullable=False)
    access = Column(Boolean, unique=False, nullable=False)




    def __str__(self) -> str:
        return f"<USER: {self.user_id, self.username, self.access}>"



class Chat(Base):
    __tablename__ = 'tg_chat'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    chatname = Column(Text, unique=False, nullable=False)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    active_chat = Column(Boolean, unique=False, nullable=False, default=False)
    add_or_left = Column(Boolean, unique=False, nullable=False, default=True)
    archiv = Column(Boolean, unique=False, nullable=False, default=False)
    chat = relationship("ChatInfo", backref='chat_info')

    def __str__(self) -> str:
        return f"<CHAT: {self.chatname, self.chat_id, self.active_chat}>"

class ChatInfo(Base):
    __tablename__ = 'chat_info'
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    chat = Column(BigInteger, ForeignKey("tg_chat.chat_id"), nullable=True, unique=True, onupdate="CASCADE")
    resident_id = Column(BigInteger, unique=False, nullable=False)
    messages = Column(Text, unique=False, nullable=True)

    def __str__(self) -> str:
        return f"<CHATINFO: {self.chat, self.resident_id, self.messages}>"


