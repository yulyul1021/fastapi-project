from sqlalchemy import Boolean, Column, Integer, String

from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    complete = Column(Boolean, default=False)


class Audio(Base):
    __tablename__ = "audio"

    id = Column(Integer, primary_key=True)
    filepath = Column(String)
    text = Column(String)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_email = Column(String, unique=True, nullable=False)  # email
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    auth_key = Column(String, unique=True, nullable=False)