from typing import List

from database import session_factory
from exceptions import UserNotFoundException, ServerNotFoundException, TariffNotFoundException

from models import User, Server, Tariff

from sqlalchemy import select

class UserRepository:
    @classmethod
    def add(cls, user: User):
        with session_factory() as session:
            session.add(user)
            session.commit()


    @classmethod
    def get(cls, chat_id: int):
        with session_factory() as session:
            user: User = session.query(User).filter(User.chat_id == chat_id).first()

            if user:
                return user
            else:
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

class ServerRepository():

    @classmethod
    def add(cls, server: Server) -> int:
        with session_factory() as session:
            session.add(server)
            session.commit()
            return server.id

    @classmethod
    def get(cls, server_id: int) -> Server:
        with session_factory() as session:
            server: Server = session.query(Server).filter(Server.id == server_id).first()
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
            tariff: Tariff = session.query(Tariff).filter(Tariff.id == tariff_id).first()
            if tariff:
                return tariff
            raise TariffNotFoundException

    @classmethod
    def remove(cls, tariff_id: int):
        with session_factory() as session:
            session.query(Tariff).filter(Tariff.id == tariff_id).delete()
            session.commit()



if __name__ == '__main__':
    server = Server(address="127.0.0.1", port=80, country="Russia")
    a = ServerRepository.add(server)
    print(ServerRepository.get_all())
    print(a)