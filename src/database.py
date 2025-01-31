from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *

engine = create_engine("sqlite:///db.db", echo=True)

session_factory = sessionmaker(engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
