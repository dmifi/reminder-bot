import re
import asyncio
import logging

from typing import NamedTuple
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook
from sqlalchemy.exc import IntegrityError

from db_map import Task, Client, session
import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """ Ответ на сообщение '/start'. Так же сохраняет пользователя в базу данных при первом обращении. """
    message_text = f"Привет {message.from_user.first_name}!\n" \
                   f"Этот бот может напомнить о небольших задачах.\n" \
                   f"Для описания работы бота введи команду /help"
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
    return SendMessage(message.from_user.id, message_text)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    """ Ответ на сообщение '/help'. """
    message_text = 'Для использования бота можно отправить сообщения вида: \n' \
                   'Во вторник почитать книгу."\n ' \
                   'По умолчанию бот напомнит о задаче в указанный день недели в 09:00'
    return SendMessage(message.from_user.id, message_text)


class ParsedMessage(NamedTuple):
    """Для сохранения даты завершения задачи и её описания. """
    completed: datetime
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
    """ Парсинг сообещния и сохранение отдельно даты и описания задачи"""
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
    """ Сохраняет в базу данных текст сообщения пользователя как задачу. """
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
        message_text = f'Привет {message.from_user.first_name}, задача "{message.text}" сохранена.'
        return SendMessage(message.from_user.id, message_text)
    except UnboundLocalError:
        session.rollback()
        message_text = f'{message.from_user.first_name}, Для использования бота можно отправить сообщения вида: \n ' \
                       f'"Во вторник почитать книгу."'
        return SendMessage(message.from_user.id, message_text)


async def sleep_and_check():
    """ Делает запрос к базе данных каждые 15 секунд.
    Отправляет пользователю текст задачи если текущее время больше установленного.
    """
    now = datetime.now()
    while True:
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
        await asyncio.sleep(15)


async def on_startup(dp):
    await bot.set_webhook(config.WEBHOOK_URL)
    asyncio.create_task(sleep_and_check())


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=config.WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
