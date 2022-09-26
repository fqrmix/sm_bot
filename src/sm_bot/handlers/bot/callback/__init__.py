from telebot import TeleBot
from sm_bot.handlers.bot.callback.shifts import *
from sm_bot.handlers.bot.callback.chatters import *
from sm_bot.handlers.bot.callback.subscription import *


def register_callback_handlers(bot: TeleBot):

    bot.register_callback_query_handler(
        handle_chatter_callback, 
        func=lambda call: call.data.startswith('chatter_') or \
                    call.data.startswith('removechatter_'), 
        pass_bot=True
    )

    bot.register_callback_query_handler(
        handle_sub_callback, 
        func=lambda call: call.data.startswith('sub_'), 
        pass_bot=True
    )

    bot.register_callback_query_handler(
        handle_dayoff_callback, 
        func=lambda call: call.data.startswith('dayoff_'), 
        pass_bot=True
    )

    bot.register_callback_query_handler(
        handle_addshift_callback,
        func=lambda call: call.data.startswith('addshift_'),
        pass_bot=True
    )

    bot.register_callback_query_handler(
        handle_swapshift_callback,
        func=lambda call: call.data.startswith('shiftswap_'),
        pass_bot=True
    )
