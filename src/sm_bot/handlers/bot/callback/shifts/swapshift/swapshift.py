from sm_bot.handlers.shiftmanager import *
from sm_bot.services.logger import logger
from telebot import types, TeleBot

def handle_swapshift_callback(call: types.CallbackQuery, bot: TeleBot):
    telegram_id = str(call.from_user.id)
    if call.data.startswith('shiftswap_user_'):
        user_shift_day = call.data.replace('shiftswap_user_day_', '')
        shiftswapper[telegram_id].shiftswap['user_shift_day'] = int(user_shift_day)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери сменщика',
            reply_markup=shiftswapper[telegram_id].build_keyboard(
                keyboard_type='shiftswap_assistant',
                telegram_id=telegram_id
            )
        )

    elif call.data.startswith('shiftswap_assistant_id_'):
        assistant_id = call.data.replace('shiftswap_assistant_id_', '')
        assistant_name, assistant_info = shiftswapper[telegram_id].get_employer_name(
            val=assistant_id,
            parameter='telegram_id',
            my_dict=shiftswapper[telegram_id].employees_info
        )
        shiftswapper[telegram_id].shiftswap['assistant_telegram_id'] = assistant_id
        shiftswapper[telegram_id].shiftswap['assistant_name'] = assistant_name

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери тип смены',
            reply_markup=shiftswapper[telegram_id].build_keyboard(
                keyboard_type='shiftswap_assistant_shift',
                telegram_id=telegram_id
            )
        )
    
    elif call.data.startswith('shiftswap_assistant_day_'):
        assistant_day = call.data.replace('shiftswap_assistant_day_', '')
        shiftswapper[telegram_id].shiftswap['assistant_shift_day'] = int(assistant_day)
        shiftswapper[telegram_id].swap_shifts()