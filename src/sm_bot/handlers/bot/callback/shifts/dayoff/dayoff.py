from sm_bot.handlers.shiftmanager import *
from sm_bot.services.logger import logger
from telebot import types, TeleBot

def handle_dayoff_callback(call: types.CallbackQuery, bot: TeleBot):
    print(call.data)
    try:
        if call.data.startswith('dayoff_start_'):
            telegram_id = str(call.from_user.id)
            dayoff_start = call.data.replace('dayoff_start_', '')
            shiftchanger[telegram_id].dayoff['telegram_id'] = telegram_id
            shiftchanger[telegram_id].dayoff['start'] = int(dayoff_start)
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='Выбери день окончания отсутствия',
                    reply_markup=shiftchanger[telegram_id].build_keyboard(
                        keyboard_type='dayoff_start', 
                        telegram_id=telegram_id, 
                        dayoff_start=dayoff_start
                    )
                )
            except Exception as e:
                print(e)
        elif call.data.startswith('dayoff_end_'):
            telegram_id = str(call.from_user.id)
            dayoff_end = call.data.replace('dayoff_end_', '')
            shiftchanger[telegram_id].dayoff['end'] = int(dayoff_end)
            shiftchanger[telegram_id].add_dayoff()
            if shiftchanger[telegram_id].dayoff['start'] == shiftchanger[telegram_id].dayoff['end']:
                dayoff_text = f"на {shiftchanger[telegram_id].dayoff['end']} число текущего месяца"
            else:
                dayoff_text = f"с {shiftchanger[telegram_id].dayoff['start']} числа по "\
                    f"{shiftchanger[telegram_id].dayoff['end']} число текущего месяца"
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Ты, {shiftchanger[telegram_id].dayoff['name']}, "\
                    f"добавил отсутствие {dayoff_text}",
                reply_markup=None
            )
    except Exception as e:
        print(e)
