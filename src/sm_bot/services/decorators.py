from telebot import types, TeleBot
import uuid
from . logger import logger

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

def message_exception_handler(func):
    def __wrapper(message: types.Message, bot: TeleBot):
        try:
            func(message, bot)
        except Exception as error:
            error_id = uuid.uuid4()
            bot.send_message(
                chat_id=message.chat.id,
                text=f'Во время обработки запроса произошла ошибка! Необходимо проверить логи.\nID: {error_id}',
                parse_mode='markdown'
            )
            logger.warn(f"Something went wrong! Error ID: {error_id}")
            logger.error(error, exc_info = True)
    return __wrapper