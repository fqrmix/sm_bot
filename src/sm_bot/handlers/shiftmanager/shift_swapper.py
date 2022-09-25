from sm_bot.handlers.workersmanager import today_workers
from sm_bot.handlers.shiftmanager import *
from sm_bot.handlers.workersmanager.employees import Employees
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sm_bot.config.config as config

class ShiftSwapper(Employees):
    def __init__(self) -> None:
        super().__init__()
        self.employees_info = config.employers_info
        self.shiftswap = {
            'user_telegram_id': str,
            'user_name': str,
            'user_shift_day': int,
            'user_shift_type': str,
            'assistant_telegram_id': str,
            'assistant_name': str,
            'assistant_shift_day': int,
            'assistant_shift_type': str
        }

    def build_keyboard(self, telegram_id: str, keyboard_type: str) -> InlineKeyboardMarkup:
            keyboard = InlineKeyboardMarkup(row_width = 2)
            buttons_list = self.create_buttons(telegram_id, keyboard_type)
            keyboard.add(*buttons_list)
            return keyboard

    def create_buttons(self, telegram_id: str, keyboard_type: str) -> list:
        buttons_list = []
        name, info = self.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=self.employees_info
            )
        self.shiftswap['user_name'] = name
        self.shiftswap['user_telegram_id'] = telegram_id

        if keyboard_type == 'shiftswap_user':
            callback_data = ''
            for employee in self.employees:
                if employee['name'] == self.shiftswap['user_name']:
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
                        callback_data = f'shiftswap_user_day_{current_day}'
                        current_button = InlineKeyboardButton(
                                text=text, 
                                callback_data=callback_data)
                        buttons_list.append(current_button)
            return buttons_list

        elif keyboard_type == 'shiftswap_assistant':
            for employee in self.employees_info:
                if employee != self.shiftswap['user_name']:
                    user_callback_data = f"shiftswap_assistant_id_{self.employees_info[employee]['telegram_id']}"
                    current_button = InlineKeyboardButton(
                            text=employee, 
                            callback_data=user_callback_data)
                    buttons_list.append(current_button)
            return buttons_list
        
        elif keyboard_type == 'shiftswap_assistant_shift':
            for employee in self.employees:
                if employee['name'] == self.shiftswap['assistant_name']:
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
                        callback_data = f'shiftswap_assistant_day_{current_day}'
                        current_button = InlineKeyboardButton(
                                text=text, 
                                callback_data=callback_data)
                        buttons_list.append(current_button)
            return buttons_list
    
    def swap_shifts(self) -> None:
        fieldnames = []
        employees = self.get_employer_list(config.CSV_PATH)
        for employee in employees:
            for current_obj in employee:
                if employee[current_obj] == self.shiftswap['user_name']:
                    for item in employee:
                        if item.isdigit() and int(item) == self.shiftswap['user_shift_day']:
                            self.shiftswap['user_shift_type'] = employee[item]
                if employee[current_obj] == self.shiftswap['assistant_name']:
                    for item in employee:
                        if item.isdigit() and int(item) == self.shiftswap['assistant_shift_day']:
                            self.shiftswap['assistant_shift_type'] = employee[item]
        print(employees, self.shiftswap)
        for employee in employees:
            for current_obj in employee:
                for item in employee:
                    if employee[current_obj] == self.shiftswap['user_name']:
                        if item.isdigit() and int(item) == self.shiftswap['user_shift_day']:
                            employee[item] = self.shiftswap['assistant_shift_type']
                    if employee[current_obj] == self.shiftswap['assistant_name']:
                        if item.isdigit() and int(item) == self.shiftswap['assistant_shift_day']:
                            employee[item] = self.shiftswap['user_shift_type']
                        fieldnames.append(item)
        self.save_employees_list(path=config.CSV_PATH, employees=employees, workers_fieldnames=fieldnames)
        today_workers._update()
