from sm_bot.handlers.shiftmanager import *
from sm_bot.services.logger import logger
from telebot import types, TeleBot

def handle_swapshift_message(message: types.Message, bot: TeleBot) -> None:
    shiftswapper[str(message.from_user.id)] = ShiftSwapper()
    bot.send_message(
            chat_id=message.chat.id, 
            text='*Выбери свою смену*', 
            reply_markup=shiftswapper[str(message.from_user.id)].build_keyboard(
                telegram_id=message.from_user.id,
                keyboard_type='shiftswap_user'
            ),
            parse_mode='Markdown'
        )
