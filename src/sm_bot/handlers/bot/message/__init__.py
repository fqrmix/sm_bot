from telebot import TeleBot
from sm_bot.handlers.bot.message.base import *
from sm_bot.handlers.bot.message.subscription.subscription import handle_sub_menu
from sm_bot.handlers.bot.message.webdav import *
from sm_bot.handlers.bot.message.workers import *
from sm_bot.handlers.bot.message.chatters import *

def register_message_handlers(bot: TeleBot):
    bot.register_message_handler(init_bot, commands=['init'], pass_bot=True)
    bot.register_message_handler(handle_lunch, commands=['lunch'], pass_bot=True)
    bot.register_message_handler(handle_log, commands=['log'], pass_bot=True)
    bot.register_message_handler(web_dav_menu, commands=['webdav'], pass_bot=True)

    # Workers
    bot.register_message_handler(handle_workers, commands=['workers'], pass_bot=True)

    # Chatters
    bot.register_message_handler(handle_chatters, commands=['chatters'], pass_bot=True)
    bot.register_message_handler(handle_add_chatters, commands=['addchatter'], pass_bot=True)
    bot.register_message_handler(handle_remove_chatters, commands=['removechatter'], pass_bot=True)

    # Sub
    bot.register_message_handler(handle_sub_menu, commands=['sub'], pass_bot=True)

    # Auto-out for lunch
    bot.register_poll_answer_handler(handle_poll_answer, func=lambda call: True, pass_bot=True)