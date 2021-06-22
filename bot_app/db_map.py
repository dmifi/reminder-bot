from sqlalchemy import Integer, String, Column, create_engine, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import re


DATABASE_URL = os.getenv("DATABASE_URL")  # or other relevant config var
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    telegram_firstname = Column(String(255))
    telegram_username = Column(String(255))

    # tasks = relationship('Task', backref='client', lazy='dynamic')

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


#
# when_to_call = 0
# client = 0
# query = session.query(Task, Client)
# query = query.join(Client, Client.id == Task.client_id)
# records = query.all()
# for task, client in records:
#     when_to_call = task.completed
#     client = client.telegram_id
# print(when_to_call, client)

# for time_to_send in session.query(Task.completed).filter(Task.completed >= datetime.datetime.now()):

#     print(time_to_send)

# time_to_send = 0
# client_to_send = 0
# telegram_id = 0

# task_alias = aliased(Task, name='task_alias')
# for row in session.query(task_alias, task_alias.completed.label('completed')).all():
#     client_to_send = row.task_alias.client_id
#     time_to_send = row.completed
#     print(client_to_send, time_to_send)

# for telegram_id in session.query(Client.telegram_id).filter(Client.id == client_to_send):
#     telegram_id = telegram_id[0]
#     print(telegram_id, client_to_send, time_to_send)

# client_alias = aliased(Client)
# task_alias = aliased(Task)
#


# for row in session.query(Task).join(Client).all():
#     print(row)

# client_to_send = Task.query.join(Client.telegram_id, aliased=True).filter_by(phenoscore=10)

# nodealias = aliased(Node)
# session.query(Node).filter(Node.data=='subchild1').\
#                 join(Node.parent.of_type(nodealias)).\
#                 filter(nodealias.data=="child2").\
#                 all()


# patients = Patient.query.join(Patient.mother, aliased=True)\
#                     .filter_by(phenoscore=10)
# client_alias = aliased(Client, name='client_alias')
# for row in session.query(client_alias, client_alias.telegram_id.label('telegram_id')).all():
#     print(row.telegram_id)

# client_alias = aliased(Client, name='client_alias')
# for row in session.query(client_alias, client_alias.telegram_firstname.label('firstname')).all():
#     print(row.client_alias, row.firstname)
#

# for instance in session.query(Client).order_by(Client.id):
#     print(instance.telegram_id, instance.telegram_firstname, instance.telegram_username)

# client_one = Client('111', "Vasiliy Pypkin", "vasia2000")
#
# task_one = Task(description='Описание задачи',
#                 created=datetime.datetime.now(tz=None),
#                 completed=datetime.datetime.now(tz=None),
#                 done=False,
#                 client_id=1)
#
# # session.add(client_one)
# # session.add(task_one)
# #
# # # ourClient = session.query(Client).filter_by(telegram_firstname="Vasiliy Pypkin").first()
# ourClient = session.query(Client).filter_by(telegram_id=6)
# print(ourClient)
# #
# # session.commit()
#
