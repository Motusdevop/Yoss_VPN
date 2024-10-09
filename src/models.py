from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (Column, Integer, String, Boolean,
                        ForeignKey, ForeignKeyConstraint,
                        DateTime, UniqueConstraint)

from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    chat_id = Column(Integer, nullable=False)
    username = Column(String)
    phone = Column(String)
    free_trial = Column(Boolean, default=True)
    role = Column(String, nullable=False, default='user')

    configs = relationship('Config', backref='user')

    # id: Mapped[int] = mapped_column(primary_key=True)
    # nickname: Mapped[str]
    # chat_id: Mapped[int] = mapped_column(nullable=False)
    # username: Mapped[str]
    # phone: Mapped[str]
    # free_trial: Mapped[bool] = mapped_column(default=True)


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    disabled = Column(Boolean, default=False)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    file = Column(String, nullable=False)

    # id: Mapped[int] = mapped_column(primary_key=True)
    # name: Mapped[str] = mapped_column(nullable=False)
    # user_id: Mapped[int] = mapped_column(nullable=False)
    # disabled: Mapped[bool] = mapped_column(default=False)
    # server_id: Mapped[int] = mapped_column(nullable=False)


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    config_id = Column(Integer, ForeignKey('configs.id'), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    expires_on = Column(DateTime())


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    country = Column(String, nullable=False)
    count_of_configs = Column(Integer, nullable=False, default=0)
    address = Column(String, nullable=False)
    port = Column(Integer, nullable=False)

class Tariff(Base):
    __tablename__ = 'tariffs'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)

