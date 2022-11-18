from sm_bot.handlers.workersmanager import today_workers
from sm_bot.handlers.workersmanager.employees import Employees
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sm_bot.config.config as config
from sm_bot.services.logger import logger
from sm_bot.services.bot import bot

class ShiftChanger(Employees):
    def __init__(self) -> None:
        super().__init__()
        self.employees_info = config.Config.employers_info
        self.dayoff = {
            'name': str,
            'telegram_id': str,
            'start': int,
            'end': int
        }
        self.shift = {
            'name': str,
            'telegram_id': str,
            'day': int,
            'type': int
        }
        

    def build_keyboard(self, keyboard_type: str, telegram_id: str, dayoff_start=None):
        if keyboard_type == 'main_dayoff':
            keyboard = InlineKeyboardMarkup(row_width = 2)
            main_menu_button_list = self.create_buttons(telegram_id=telegram_id)
            keyboard.add(*main_menu_button_list)
            return keyboard
        
        if keyboard_type == 'dayoff_start':
            try:
                keyboard = InlineKeyboardMarkup(row_width = 2)
                main_menu_button_list = self.create_buttons(
                    telegram_id=telegram_id, 
                    dayoff_start=dayoff_start
                )
                keyboard.add(*main_menu_button_list)
                return keyboard
            except Exception as e:
                print(e)
        
        if keyboard_type == 'addshift_main':
            keyboard = InlineKeyboardMarkup(row_width=2)
            main_menu_button_list = self.create_buttons(
                telegram_id=telegram_id,
                add_shift=True
            )
            keyboard.add(*main_menu_button_list)
            return keyboard

        if keyboard_type == 'addshift_list':
            keyboard = InlineKeyboardMarkup(row_width=3)
            main_menu_button_list = self.create_shift_buttons()
            keyboard.add(*main_menu_button_list)
            return keyboard


    def create_buttons(self, telegram_id: str, dayoff_start=None, add_shift=False) -> list:
        text = ''
        start = ''
        end = ''
        callback_data = ''
        main_menu_button_list = []
        name, info = self.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=self.employees_info
            )
        if not add_shift:
            self.dayoff['name'] = name
        else:
            self.shift['name'] = name
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
                            start = config.Config.working_shift[current_shift[0]]['start']
                            end = config.Config.working_shift[current_shift[0]]['end']
                            text = f"{current_day} | {start} - {end}"
                    else:
                        text = current_day
                    if dayoff_start is not None:
                        if dayoff_start == current_day:
                            text += '\n[Начало]'
                        callback_data = f'dayoff_end_{current_day}'
                    else:
                        if not add_shift:
                            callback_data = f'dayoff_start_{current_day}'
                        else:
                            callback_data = f'addshift_{current_day}'
                    current_button = InlineKeyboardButton(
                            text=text, 
                            callback_data=callback_data)
                    main_menu_button_list.append(current_button)
        return main_menu_button_list
    
    def create_shift_buttons(self) -> list:
        main_menu_button_list = []
        text: str
        for type in config.Config.working_shift:
            text = f"{config.Config.working_shift[type]['start']} - {config.Config.working_shift[type]['end']}"
            current_button = InlineKeyboardButton(
                text=text,
                callback_data=f"addshift_type_{type}"
            )
            main_menu_button_list.append(current_button)
        return main_menu_button_list
        
    def add_dayoff(self) -> None:
        employees = self.get_employer_list(config.Config.CSV_PATH)
        fieldnames = []
        if self.dayoff['start'] > self.dayoff['end']:
            self.dayoff['start'], self.dayoff['end'] = self.dayoff['end'], self.dayoff['start']
        for employee in employees:
            for current_obj in employee:
                if employee[current_obj] == self.dayoff['name']:
                    for item in employee:
                        if item.isdigit() and int(item) in range(self.dayoff['start'], self.dayoff['end'] + 1):
                            employee[item] = 'DO'
                        fieldnames.append(item)
        self.save_employees_list(path=config.Config.CSV_PATH, employees=employees, workers_fieldnames=fieldnames)
        today_workers._update()

    def add_shift(self) -> None:
        employees = self.get_employer_list(config.Config.CSV_PATH)
        fieldnames = []
        for employee in employees:
            for current_obj in employee:
                if employee[current_obj] == self.shift['name']:
                    for item in employee:
                        if item.isdigit() and int(item) == self.shift['day']:
                            employee[item] = self.shift['type']
                        fieldnames.append(item)
        self.save_employees_list(path=config.Config.CSV_PATH, employees=employees, workers_fieldnames=fieldnames)
        today_workers._update()
