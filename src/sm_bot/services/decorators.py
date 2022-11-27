from telebot import types, TeleBot
import uuid
from . logger import logger
from sm_bot.services.bot import bot
import sm_bot.config.config as config

def on_private_chat_only(send_message):
    def __wrapper(message: types.Message, bot: TeleBot):
        if message.chat.type != 'private':
            bot.send_message(
                chat_id=message.chat.id, 
                text='Эта функция предназначена только для использания в личке у бота!',
                parse_mode='Markdown'
            )
        else:
            send_message(message, bot)
    return __wrapper

def exception_handler(func):
    def __wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as error:
            error_id = uuid.uuid4()
            bot.send_message(
                chat_id=config.Config.GROUP_CHAT_ID_SM,
                text=f'Во время обработки произошла ошибка!\n'\
                    f'Необходимо проверить логи.\n'\
                    f'Method name: {func.__qualname__}\n'\
                    f'\nID: {error_id}\nError: {error}',
                parse_mode='markdown'
            )
            logger.warn(f"Something went wrong! Error ID: {error_id}")
            logger.error(error, exc_info = True)
    return __wrapper
