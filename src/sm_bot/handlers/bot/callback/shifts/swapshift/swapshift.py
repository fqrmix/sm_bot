from sm_bot.handlers.shiftmanager import *
from sm_bot.services.logger import logger
from sm_bot.config import config
from telebot import types, TeleBot

def handle_swapshift_callback(call: types.CallbackQuery, bot: TeleBot):
    telegram_id = str(call.from_user.id)
    if call.data.startswith('shiftswap_user_'):
        user_shift_day = call.data.replace('shiftswap_user_day_', '')
        shiftswapper[telegram_id].shiftswap['user_shift_day'] = int(user_shift_day)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='*Выбери сменщика*',
            reply_markup=shiftswapper[telegram_id].build_keyboard(
                keyboard_type='shiftswap_assistant',
                telegram_id=telegram_id
            ),
            parse_mode='markdown'
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
            text='*Выбери смену сменщика*',
            reply_markup=shiftswapper[telegram_id].build_keyboard(
                keyboard_type='shiftswap_assistant_shift',
                telegram_id=telegram_id
            ),
            parse_mode='markdown'
        )
    
    elif call.data.startswith('shiftswap_assistant_day_'):
        assistant_day = call.data.replace('shiftswap_assistant_day_', '')
        shiftswapper[telegram_id].shiftswap['assistant_shift_day'] = int(assistant_day)
        shiftswapper[telegram_id].swap_shifts()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="*Ты успешно поменялся сменами:*\n\n"\
                f"{shiftswapper[telegram_id].shiftswap['user_name']} | "\
                f"*Число:* {shiftswapper[telegram_id].shiftswap['user_shift_day']} | "\
                f"*Смена:* {config.Config.working_shift[shiftswapper[telegram_id].shiftswap['user_shift_type'][0]]['start']} : "\
                f"{config.Config.working_shift[shiftswapper[telegram_id].shiftswap['user_shift_type'][0]]['end']}"
                f"\n🔁🔁🔁\n"\
                f"{shiftswapper[telegram_id].shiftswap['assistant_name']} | "\
                f"*Число:* {shiftswapper[telegram_id].shiftswap['assistant_shift_day']} | "\
                f"*Смена:* {config.Config.working_shift[shiftswapper[telegram_id].shiftswap['assistant_shift_type'][0]]['start']} : "\
                f"{config.Config.working_shift[shiftswapper[telegram_id].shiftswap['assistant_shift_type'][0]]['end']}",
            reply_markup=None,
            parse_mode='markdown'
        )