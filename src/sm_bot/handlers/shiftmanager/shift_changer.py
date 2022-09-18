from sm_bot.handlers.workersmanager.employees import Employees
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sm_bot.config.config as config
from sm_bot.services.logger import logger
from sm_bot.services.bot import bot

class ShiftChanger(Employees):
    def __init__(self) -> None:
        super().__init__()
        self.employees_info = config.employers_info
        self.dayoff_list = []
        self.dayoff = {
            'name': str,
            'telegram_id': str,
            'start': int,
            'end': int
        }
        

    def build_keyboard(self, keyboard_type, telegram_id, dayoff_start=None):
        if keyboard_type == 'main_dayoff':
            keyboard = InlineKeyboardMarkup(row_width = 2)
            main_menu_button_list = self.create_button_list(telegram_id=telegram_id)
            keyboard.add(*main_menu_button_list)
            return keyboard
        if keyboard_type == 'dayoff_start':
            try:
                keyboard = InlineKeyboardMarkup(row_width = 2)
                main_menu_button_list = self.create_button_list(
                    telegram_id=telegram_id, 
                    dayoff_start=dayoff_start
                )
                keyboard.add(*main_menu_button_list)
                return keyboard
            except Exception as e:
                print(e)
        
    def create_button_list(self, telegram_id, dayoff_start=None):
        text = ''
        start = ''
        end = ''
        callback_data = ''
        main_menu_button_list = []
        name, info = Employees.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=self.employees_info
            )
        self.dayoff['name'] = name
        for employee in self.employees:
            if employee['name'] == name:
                for current_day in employee['shifts']:
                    current_shift = employee['shifts'][current_day]
                    if current_shift != '':
                        if current_shift == 'DO':
                            text = f"{current_day} | Dayoff"
                        elif current_shift == 'ОТ':
                            text = f"{current_day} | Отпуск"
                        else:
                            start = config.working_shift[current_shift[0]]['start']
                            end = config.working_shift[current_shift[0]]['end']
                            text = f"{current_day} | {start} - {end}"
                    else:
                        text = current_day
                    if dayoff_start is not None:
                        if dayoff_start == current_day:
                            text += '\n[Начало]'
                        callback_data = f'dayoff_end_{current_day}'
                    else:
                        callback_data = f'dayoff_start_{current_day}'
                    current_button = InlineKeyboardButton(
                            text=text, 
                            callback_data=callback_data)
                    main_menu_button_list.append(current_button)
        return main_menu_button_list

telegram_token = '5316952420:AAHpY4Jp43C0DrK0uQNHvomDZ9XhDW3aLBU'

shiftchanger = {0: ShiftChanger}

@bot.message_handler(commands=['dayoff'])
def send_first_dayoff_message(message):
    shiftchanger[str(message.from_user.id)] = ShiftChanger()
    bot.send_message(
            chat_id=message.chat.id, 
            text='Выбери день начала отсутствия', 
            reply_markup=shiftchanger[str(message.from_user.id)].build_keyboard(
                keyboard_type='main_dayoff', 
                telegram_id=message.from_user.id
            )
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data.startswith('dayoff_start_'):
            telegram_id = str(call.from_user.id)
            dayoff_start = call.data.replace('dayoff_start_', '')
            shiftchanger[telegram_id].dayoff['telegram_id'] = telegram_id
            shiftchanger[telegram_id].dayoff['start'] = int(dayoff_start)

            inner_message = bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text='Выбери день окончания отсутствия',
                        reply_markup=shiftchanger[telegram_id].build_keyboard(
                            keyboard_type='dayoff_start', 
                            telegram_id=telegram_id, 
                            dayoff_start=dayoff_start
                        )
                    )
        elif call.data.startswith('dayoff_end_'):
            telegram_id = str(call.from_user.id)
            dayoff_end = call.data.replace('dayoff_end_', '')
            shiftchanger[telegram_id].dayoff['end'] = int(dayoff_end)
            if shiftchanger[telegram_id].dayoff['start'] == shiftchanger[telegram_id].dayoff['end']:
                dayoff_text = f"на {shiftchanger[telegram_id].dayoff['end']} число текущего месяца"
            else:
                dayoff_text = f"с {shiftchanger[telegram_id].dayoff['start']} числа по "\
                    f"{shiftchanger[telegram_id].dayoff['end']} число текущего месяца"
            inner_message = bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"Ты, {shiftchanger[telegram_id].dayoff['name']}, "\
                            f"добавил отсутствие {dayoff_text}",
                        reply_markup=None
                    )
            shiftchanger[telegram_id].add_dayoff(shiftchanger[telegram_id].dayoff)
    except Exception as e:
        print(e)

bot.infinity_polling(skip_pending = True)
