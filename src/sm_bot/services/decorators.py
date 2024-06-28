from telebot import types, TeleBot
import uuid
from . logger import logger
from sm_bot.services.bot import bot
import sm_bot.config.config as config

def b2btech_only(send_message):
    def __wrapper(message: types.Message, bot: TeleBot):
        b2btech_user = False
        for info in config.Config.employers_info.values():
            if info['telegram_id'] == str(message.from_user.id):
                b2btech_user = True
        if not b2btech_user:
            bot.send_message(
                chat_id=message.chat.id, 
                text='Эта функция предназначена только для сотрудников b2b_tech!',
            )
        else:
            return send_message(message, bot)
    return __wrapper

def admin_only(send_message):
    def __wrapper(message: types.Message, bot: TeleBot):
        if message.from_user.id not in [966243980, 818727118, 361925429]:
            bot.send_message(
                chat_id=message.chat.id, 
                text='Эта функция предназначена только для админинстратора бота!',
            )
        else:
            return send_message(message, bot)
    return __wrapper

def on_private_chat_only(send_message):
    def __wrapper(message: types.Message, bot: TeleBot):
        if message.chat.type != 'private':
            bot.send_message(
                chat_id=message.chat.id, 
                text='Эта функция предназначена только для использания в личке у бота!',
                parse_mode='Markdown'
            )
        else:
            return send_message(message, bot)
    return __wrapper

def exception_handler(func):
    def __wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as error:
            error_id = uuid.uuid4()
            bot.send_message(
                chat_id=966243980,
                text=f'Во время обработки произошла ошибка!\n'\
                    f'Необходимо проверить логи.\n'\
                    f'Method name: {func.__qualname__}\n'\
                    f'\nID: {error_id}\nError: {error}',
                parse_mode='markdown'
            )
            logger.warn(f"Something went wrong! Error ID: {error_id}")
            logger.error(error, exc_info = True)
    return __wrapper
