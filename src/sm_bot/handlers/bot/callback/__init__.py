from telebot import TeleBot
from sm_bot.handlers.bot.callback.subscription import *
from sm_bot.handlers.bot.callback.chatters import *


def register_callback_handlers(bot: TeleBot):
    bot.register_callback_query_handler(handle_sub_callback, func=lambda call: True, pass_bot=True)
    bot.register_callback_query_handler(handle_chatter_callback, func=lambda call: True, pass_bot=True)
