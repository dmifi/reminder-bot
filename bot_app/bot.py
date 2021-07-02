import re
import asyncio

from typing import NamedTuple
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from sqlalchemy.exc import IntegrityError

from db_map import Task, Client, session
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """ Функция сохраняет пользователя в базу данных при первом обращении.
    """
    await message.reply(
        f"Привет %s!\n"
        f"Этот бот может напомнить о небольших задачах.\n"
        f"Для описания работы бота введи команду /help" % message.from_user.first_name)
    client = Client(
        telegram_id=message.from_user.id,
        telegram_firstname=message.from_user.first_name,
        telegram_username=message.from_user.username
    )
    session.add(client)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(
        f'Для использования бота можно отправить сообщения вида: \n'
        f'"Во вторник почитать книгу."\n'
        f'По умолчанию бот напомнит о задаче в указанный день недели в 09:00')


class ParsedMessage(NamedTuple):
    """Класс для хранения времени и описания задачи.
    """
    completed: str
    description: str


def get_completed(task_completed):
    now = datetime.now()
    days_list = ['в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу', 'в воскресенье',
                 'завтра', 'послезавтра']
    days_dict = dict(zip(days_list, [a for a in range(7)]))
    day_of_next_week = now + timedelta(days=days_dict[task_completed] - now.weekday(), weeks=1)
    day_of_this_week = now + timedelta(days=days_dict[task_completed] - now.weekday())
    if day_of_next_week - now <= timedelta(days=7):
        day_completed = day_of_next_week.replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        day_completed = day_of_this_week.replace(hour=9, minute=0, second=0, microsecond=0)
    return day_completed


def parse_message(message):
    days_list = ['в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу', 'в воскресенье',
                 'завтра', 'послезавтра']
    for day in days_list:
        completed = re.match(f"(%s)(.*)" % day, message, re.IGNORECASE)
        if completed and completed.group(1) and completed.group(2) is not None:
            task_completed = completed.group(1).lower()
            day_completed = get_completed(task_completed)
            description = completed.group(2).lstrip().capitalize()
    return ParsedMessage(completed=day_completed, description=description)


@dp.message_handler()
async def save_message(message: types.Message):
    """Сохраняет в базу данных текст сообщения пользователя как задачу.
    """
    telegram_id = 0
    for telegram_id in session.query(Client.id).filter(Client.telegram_id == message.from_user.id):
        telegram_id = telegram_id[0]
    try:
        parsed_message = parse_message(message.text)
        task = Task(
            description=parsed_message.description,
            created=datetime.now(),
            completed=parsed_message.completed,
            done=False,
            client_id=telegram_id
        )
        session.add(task)
        session.commit()
        await bot.send_message(message.from_user.id,
                               f'Привет %s, задача "%s" сохранена.' % (message.from_user.first_name, message.text))
    except UnboundLocalError:
        await bot.send_message(message.from_user.id, f'%s, Для использования бота можно отправить сообщения вида: \n'
                                                     f'"Во вторник почитать книгу."' % message.from_user.first_name)
        session.rollback()


async def sleep_and_check(seconds_to_wait):
    """ Делает запрос к базе данных каждые 'seconds_to_wait' секунд.
    Отправляет пользователю текст задачи если текущее время больше установленного.
    """
    now = datetime.now()
    while True:
        await asyncio.sleep(seconds_to_wait)
        query = session.query(Task, Client)
        query = query.join(Client, Client.id == Task.client_id)
        records = query.all()
        for task, client in records:
            if task.done is False and now >= task.completed:
                await bot.send_message(
                    chat_id=client.telegram_id,
                    text=task.description)
                task.done = True
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
            else:
                session.rollback()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(sleep_and_check(15))
    executor.start_polling(dp)
