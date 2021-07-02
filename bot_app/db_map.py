from sqlalchemy import Integer, String, Column, create_engine, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import config

Base = declarative_base()
engine = create_engine(config.DATABASE_URL, echo=True)


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    telegram_firstname = Column(String(255))
    telegram_username = Column(String(255))

    def __init__(self, telegram_id, telegram_firstname, telegram_username):
        self.telegram_id = telegram_id
        self.telegram_firstname = telegram_firstname
        self.telegram_username = telegram_username

    def __repr__(self):
        return '<Client("%s", "%s, "%s">' % (self.telegram_id, self.telegram_firstname, self.telegram_username)


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    description = Column(String(1000))
    created = Column(DateTime(timezone=False))
    completed = Column(DateTime(timezone=False))
    done = Column(Boolean)
    client_id = Column(ForeignKey('client.id'), nullable=False)
    client = relationship(Client)

    def __init__(self, description, created, completed, done, client_id):
        self.description = description
        self.created = created
        self.completed = completed
        self.done = done
        self.client_id = client_id

    def __repr__(self):
        return '<Task("%s", "%s, "%s", "%s", "%s">' % (
            self.description, self.created, self.completed, self.done, self.client_id)


Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)

session = Session()
