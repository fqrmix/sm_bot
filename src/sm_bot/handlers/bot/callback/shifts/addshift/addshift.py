from sm_bot.handlers.shiftmanager import *
from sm_bot.config import config
from sm_bot.services.logger import logger
from telebot import types, TeleBot

def handle_addshift_callback(call: types.CallbackQuery, bot: TeleBot):
    try:
        if call.data.startswith('addshift_type_'):
            telegram_id = str(call.from_user.id)
            shift_type = call.data.replace('addshift_type_', '')
            shiftchanger[telegram_id].shift['type'] = shift_type
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"*Ты успешно добавил смену "\
                    f"{config.Config.working_shift[shiftchanger[telegram_id].shift['type'][0]]['start']} - "\
                    f"{config.Config.working_shift[shiftchanger[telegram_id].shift['type'][0]]['end']}*",
                reply_markup=None,
                parse_mode='Markdown'
                
            )
            shiftchanger[telegram_id].add_shift()
    
        elif call.data.startswith('addshift_'):
            telegram_id = str(call.from_user.id)
            print(shiftchanger[telegram_id])
            addshift_day = call.data.replace('addshift_', '')
            shiftchanger[telegram_id].shift['telegram_id'] = telegram_id
            shiftchanger[telegram_id].shift['day'] = int(addshift_day)

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='*Выбери тип смены*',
                reply_markup=shiftchanger[telegram_id].build_keyboard(
                    keyboard_type='addshift_list',
                    telegram_id=telegram_id
                ),
                parse_mode='Markdown'
            )


    except Exception as e:
        print(e)
