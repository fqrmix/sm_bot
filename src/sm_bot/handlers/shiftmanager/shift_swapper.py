from sm_bot.handlers.workersmanager import today_workers
from sm_bot.handlers.shiftmanager import *
from sm_bot.handlers.workersmanager.employees import Employees
from sm_bot.services.logger import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sm_bot.config.config as config

class ShiftSwapper(Employees):
    def __init__(self) -> None:
        super().__init__()
        self.employees_info = config.Config.employers_info
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
        try:
            keyboard = InlineKeyboardMarkup(row_width = 2)
            buttons_list = self.create_buttons(telegram_id, keyboard_type)
            keyboard.add(*buttons_list)
            return keyboard
        except Exception as error:
            logger.error(error, exc_info=True)            

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
                                start = config.Config.working_shift[current_shift[0]]['start']
                                end = config.Config.working_shift[current_shift[0]]['end']
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
            for employee in self.employees:
                if employee['name'] != self.shiftswap['user_name']:
                    user_callback_data = f"shiftswap_assistant_id_{self.employees_info[employee['name']]['telegram_id']}"
                    current_button = InlineKeyboardButton(
                            text=employee['name'], 
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
                                start = config.Config.working_shift[current_shift[0]]['start']
                                end = config.Config.working_shift[current_shift[0]]['end']
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
        try:
            fieldnames = []
            employees = self.get_employer_list(config.Config.CSV_PATH)
            for employee in employees:
                for current_obj in employee:
                    if employee[current_obj] == self.shiftswap['user_name']:
                        for item in employee:
                            if item.isdigit() and int(item) == self.shiftswap['user_shift_day']:
                                self.shiftswap['user_shift_type'] = employee[item]
                                logger.info(f"[shiftswapper] | [{self.shiftswap['user_name']}] "\
                                    f"User shift type was found: {self.shiftswap['user_shift_type']}")
                    if employee[current_obj] == self.shiftswap['assistant_name']:
                        for item in employee:
                            if item.isdigit() and int(item) == self.shiftswap['assistant_shift_day']:
                                self.shiftswap['assistant_shift_type'] = employee[item]
                                logger.info(f"[shiftswapper] | [{self.shiftswap['user_name']}]"\
                                        f"Assistant [{self.shiftswap['assistant_name']}] shift type was found:"\
                                        f"{self.shiftswap['assistant_shift_type']}")
            for employee in employees:
                for current_obj in employee:
                    for item in employee:
                        if employee[current_obj] == self.shiftswap['user_name']:
                            if item.isdigit() and int(item) == self.shiftswap['user_shift_day']:
                                employee[item] = self.shiftswap['assistant_shift_type']
                                logger.info(f"[shiftswapper] | [{self.shiftswap['user_name']}] "\
                                    f"User shift [{self.shiftswap['user_shift_type']}] was successfully replaced by "\
                                    f"[[{self.shiftswap['assistant_name']}]] shift: {self.shiftswap['assistant_shift_type']}")
                        if employee[current_obj] == self.shiftswap['assistant_name']:
                            if item.isdigit() and int(item) == self.shiftswap['assistant_shift_day']:
                                employee[item] = self.shiftswap['user_shift_type']
                                logger.info(f"[shiftswapper] | [{self.shiftswap['user_name']}] "\
                                    f"Assistant shift [{self.shiftswap['assistant_name']}] was successfully replaced by "\
                                    f"[[{self.shiftswap['user_name']}]] shift: {self.shiftswap['user_shift_type']}")
                            fieldnames.append(item)
            self.save_employees_list(path=config.Config.CSV_PATH, employees=employees, workers_fieldnames=fieldnames)
            today_workers._update()
        except Exception as error:
            logger.error(error, exc_info=True)
