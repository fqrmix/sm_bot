from sm_bot.handlers.shiftmanager import *
from sm_bot.services.logger import logger
from telebot import types, TeleBot
from sm_bot.services.decorators import on_private_chat_only

@on_private_chat_only
def handle_dayoff_message(message: types.Message, bot: TeleBot):
    shiftchanger[str(message.from_user.id)] = ShiftChanger()
    bot.send_message(
            chat_id=message.chat.id, 
            text='*Выбери день начала отсутствия*', 
            reply_markup=shiftchanger[str(message.from_user.id)].build_keyboard(
                keyboard_type='main_dayoff', 
                telegram_id=message.from_user.id
            ),
            parse_mode='Markdown'
        )
