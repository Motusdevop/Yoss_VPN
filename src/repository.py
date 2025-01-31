from datetime import datetime
from typing import List

from sqlalchemy import select, update

from database import session_factory
from exceptions import (
    ConfigNotFoundException,
    ServerNotFoundException,
    SubscriptionNotFoundException,
    TariffNotFoundException,
    TransactionNotFoundException,
    UserNotFoundException,
)
from models import Config, Server, Subscription, Tariff, Transaction, User


class UserRepository:
    @classmethod
    def add(cls, user: User):
        with session_factory() as session:
            session.add(user)
            session.commit()

    @classmethod
    def get_from_chat_id(cls, chat_id: int):
        with session_factory() as session:
            user: User = session.query(User).filter(User.chat_id == chat_id).first()

            if user:
                return user
            raise UserNotFoundException

    @classmethod
    def get(cls, user_id: int):
        with session_factory() as session:
            user: User = session.query(User).filter(User.id == user_id).first()

            if user:
                return user
            raise UserNotFoundException

    @classmethod
    def make_admin(cls, chat_id: int):
        with session_factory() as session:
            user: User = session.query(User).filter(User.chat_id == chat_id).first()
            if user:
                user.role = "admin"
                session.commit()
            else:
                raise UserNotFoundException

    @classmethod
    def check_registration(cls, chat_id: int) -> bool:
        with session_factory() as session:
            query = select(User).where(User.chat_id == chat_id)

            result = session.execute(query)

            if result.one_or_none():
                return True
            else:
                return False

    @classmethod
    def get_admins(cls) -> List[User]:
        with session_factory() as session:
            res: List[User] = session.query(User).filter(User.role == "admin").all()
            return res

    @classmethod
    def update(cls, user_id: int, **kwargs):
        with session_factory() as session:
            query = update(User).where(User.id == user_id).values(**kwargs)
            session.execute(query)
            session.commit()

    @classmethod
    def get_all(cls) -> List[User]:
        with session_factory() as session:
            res = session.query(User).all()
            return res

    @classmethod
    def delete(cls, user_id: int):
        with session_factory() as session:
            session.query(User).filter(User.id == user_id).delete()
            session.commit()


class ServerRepository:

    @classmethod
    def add(cls, server: Server) -> int:
        with session_factory() as session:
            session.add(server)
            session.commit()
            return server.id

    @classmethod
    def get(cls, server_id: int) -> Server:
        with session_factory() as session:
            server: Server = (
                session.query(Server).filter(Server.id == server_id).first()
            )
            if server:
                return server
            raise ServerNotFoundException

    @classmethod
    def get_all(cls) -> List[Server]:
        with session_factory() as session:
            res = session.query(Server).all()
            return res

    @classmethod
    def remove(cls, server_id: int):
        with session_factory() as session:
            session.query(Server).filter(Server.id == server_id).delete()
            session.commit()

    @classmethod
    def update(cls, server_id: int, **kwargs):
        with session_factory() as session:
            query = update(Server).where(Server.id == server_id).values(**kwargs)
            session.execute(query)
            session.commit()


class TariffRepository:
    @classmethod
    def get_all(cls) -> List[Tariff]:
        with session_factory() as session:
            res = session.query(Tariff).all()
            return res

    @classmethod
    def add(cls, tariff: Tariff):
        with session_factory() as session:
            session.add(tariff)
            session.commit()

    @classmethod
    def get(cls, tariff_id: int) -> Tariff:
        with session_factory() as session:
            tariff: Tariff = (
                session.query(Tariff).filter(Tariff.id == tariff_id).first()
            )
            if tariff:
                return tariff
            raise TariffNotFoundException

    @classmethod
    def remove(cls, tariff_id: int):
        with session_factory() as session:
            session.query(Tariff).filter(Tariff.id == tariff_id).delete()
            session.commit()


class TransactionRepository:
    @classmethod
    def add(cls, transaction: Transaction):
        with session_factory() as session:
            session.add(transaction)
            session.commit()

    @classmethod
    def get(cls, transaction_id: int) -> Transaction:
        with session_factory() as session:
            transaction: Transaction = (
                session.query(Transaction)
                .filter(Transaction.id == transaction_id)
                .first()
            )
            if transaction:
                return transaction
            raise TransactionNotFoundException

    @classmethod
    def get_all(cls) -> List[Transaction]:
        with session_factory() as session:
            res = session.query(Transaction).all()
            return res

    @classmethod
    def remove(cls, transaction_id: int):
        with session_factory() as session:
            session.query(Transaction).filter(Transaction.id == transaction_id).delete()
            session.commit()

    @classmethod
    def get_from_user_id(cls, user_id: int) -> List[Transaction]:
        with session_factory() as session:
            transactions: List[Transaction] = (
                session.query(Transaction).filter(Transaction.user_id == user_id).all()
            )
            return transactions

    @classmethod
    def delete(cls, transaction_id: int):
        with session_factory() as session:
            session.query(Transaction).filter(Transaction.id == transaction_id).delete()
            session.commit()


class SubscriptionRepository:
    @classmethod
    def add(cls, subscription: Subscription) -> int:
        with session_factory() as session:
            session.add(subscription)
            session.commit()
            return subscription.id

    @classmethod
    def get(cls, subscription_id: int) -> Subscription:
        with session_factory() as session:
            subscription: Subscription = (
                session.query(Subscription)
                .filter(Subscription.id == subscription_id)
                .first()
            )
            if subscription:
                return subscription
            raise SubscriptionNotFoundException

    @classmethod
    def get_from_user_id(cls, user_id: int) -> List[Subscription]:
        with session_factory() as session:
            subscriptions: List[Subscription] = (
                session.query(Subscription)
                .filter(Subscription.user_id == user_id)
                .all()
            )
            return subscriptions

    @classmethod
    def set_expired_on(cls, subscription_id: int, new_expires_on: datetime):
        with session_factory() as session:
            query = (
                session.query(Subscription)
                .filter(Subscription.id == subscription_id)
                .update({"expires_on": new_expires_on})
            )
            session.commit()

    @classmethod
    def get_all(cls) -> List[Subscription]:
        with session_factory() as session:
            res = session.query(Subscription).all()
            return res

    @classmethod
    def delete(cls, subscription_id: int):
        with session_factory() as session:
            session.query(Subscription).filter(
                Subscription.id == subscription_id
            ).delete()
            session.commit()


class ConfigRepository:
    @classmethod
    def add(cls, config: Config) -> int:
        with session_factory() as session:
            session.add(config)
            session.commit()
            return config.id

    @classmethod
    def get(cls, config_id: int) -> Config:
        with session_factory() as session:
            config: Config = (
                session.query(Config).filter(Config.id == config_id).first()
            )

            if config:
                return config
            raise ConfigNotFoundException

    @classmethod
    def update(cls, config_id, **kwargs):
        with session_factory() as session:
            query = update(Config).where(Config.id == int(config_id)).values(**kwargs)
            session.execute(query)
            session.commit()

    @classmethod
    def delete(cls, config_id: int):
        with session_factory() as session:
            session.query(Config).filter(Config.id == config_id).delete()
            session.commit()

    @classmethod
    def get_from_user_id(cls, user_id: int) -> List[Config]:
        with session_factory() as session:
            configs: List[Config] = (
                session.query(Config).filter(Config.user_id == user_id).all()
            )
            return configs


if __name__ == "__main__":
    server = Server(address="127.0.0.1", port=80, country="Russia")
    a = ServerRepository.add(server)
    print(ServerRepository.get_all())
    print(a)
