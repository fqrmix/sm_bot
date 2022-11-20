import calendar
import schedule
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sm_bot.config as config
from sm_bot.services.logger import logger
from sm_bot.services.bot import bot
from sm_bot.handlers.workersmanager.employees import Employees
from sm_bot.handlers.workersmanager.day_workers import DayWorkers


########################
##### Subscription #####
########################

class Subscription:
    @classmethod
    def __init__(cls, test_run=False):
        current_employee_sub = {}
        cls.active_sub_list = []
        cls.employees_info = config.Config.employers_info
        cls.test_run = test_run
        for employee in cls.employees_info:
            current_employee = cls.employees_info[employee]
            if current_employee['subscription']['enabled'] == True:
                current_employee_sub['name'] = employee
                current_employee_sub['telegram_id'] = current_employee['telegram_id']
                current_employee_sub['time_to_notify'] = current_employee['subscription']['time_to_notify']
                cls.active_sub_list.append(current_employee_sub)
                current_employee_sub = {}
        logger.info(msg=f"[Sub] Subscription class was initialized. Found active subs:\n{cls.get_active_subs()}")

    @classmethod
    def get_active_subs(cls):
        return cls.active_sub_list

    @classmethod
    def save_sub(cls):
        try:
            with open(config.Config.JSON_DIR_PATH + 'employers_info.json', 'w', encoding='utf-8') as info_json:    
                config.json.dump(cls.employees_info, info_json, indent=4, ensure_ascii=False)
            logger.info(msg="[sub] Subscription JSON info was dumped to server")
        except Exception as error:
            logger.error(error, exc_info = True)
        
    @classmethod
    def get_sub_info(cls, telegram_id):
        try:
            name, info = Employees.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=cls.employees_info
            )
            for employee in cls.employees_info:
                current_employee = cls.employees_info[employee]
                if employee == name:
                    logger.info(msg=f"[Sub] Found subscription info for userID: {telegram_id}")
                    return current_employee['subscription']
        except Exception as error:
            logger.error(error, exc_info = True)

    @classmethod
    def disable(cls, telegram_id):
        try:
            name, info = Employees.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=cls.employees_info
            )
            cls.employees_info[name]['subscription']['enabled'] = False
            cls.save_sub()
            logger.info(msg=f"[Sub] Subscription was disabled for userID: {telegram_id}")
            return cls.employees_info[name]['subscription']
        except Exception as error:
            logger.error(error, exc_info = True)

    @classmethod
    def enable(cls, telegram_id):
        try:
            name, info = Employees.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=cls.employees_info
            )
            cls.employees_info[name]['subscription']['enabled'] = True
            cls.save_sub()
            logger.info(msg=f"[Sub] Subscription was enabled for userID: {telegram_id}")
            return cls.employees_info[name]['subscription']
        except Exception as error:
            logger.error(error, exc_info = True)

    @classmethod
    def change_notification_time(cls, telegram_id, time):
        try:
            name, info = Employees.get_employer_name(
                val=str(telegram_id),
                parameter='telegram_id',
                my_dict=cls.employees_info
            )
            cls.employees_info[name]['subscription']['time_to_notify'] = time
            cls.save_sub()
            logger.info(msg=f"[Sub] Time for subscription was changed to {time} for userID: {telegram_id}")
            return cls.employees_info[name]['subscription']
        except Exception as error:
            logger.error(error, exc_info = True)
    
    @classmethod
    def __sending_job__(cls, actual_employee):
        try:
            bot.send_message(
                    chat_id = actual_employee['telegram_id'],
                    parse_mode = "Markdown",
                    text = f"Привет!\nТы завтра работаешь с {actual_employee['shift_start']} "\
                        f"до {actual_employee['shift_end']}"
                )
            logger.info(msg=f"[Sub] Subscription message was send to user: {actual_employee['name']}")
            return schedule.CancelJob
        except Exception as error:
            bot.send_message(
                    chat_id = actual_employee['telegram_id'],
                    text = f"Exception raised! Check log file for detailed info."
                )
            logger.error(error, exc_info = True)

    @classmethod
    def create_schedule(cls) -> schedule:
        try:
            now = datetime.datetime.now()
            current_month_days = calendar.monthrange(now.year, now.month)[1]
            if datetime.date.today().day + 1 > current_month_days:
                day = '1'
                all_employees = Employees(next_month=True)
            else:
                day = str(datetime.date.today().day + 1)
                all_employees = Employees()
            for current_employee_sub in cls.active_sub_list:
                for current_employee in all_employees.employees:
                    if current_employee['name'] == current_employee_sub['name']:
                        if current_employee['shifts'][day] != "" \
                        and current_employee['shifts'][day] != "ОТ":
                            actual_employee = DayWorkers.create_actual_employee(current_employee, day)
                            actual_schedule = schedule.every().day.at(current_employee_sub['time_to_notify']).do(
                                cls.__sending_job__,
                                actual_employee=actual_employee
                            )
                            logger.info(
                                msg=f"[Sub] Schedule for {current_employee_sub['name']} was created," \
                                    f" time: {current_employee_sub['time_to_notify']}")
        except Exception as error:
            logger.error(error, exc_info = True)
            return None

    @classmethod
    def handle_change_subtime(cls, message, telegram_id):
        splited_time = message.text.split(':')
        if len(splited_time) < 2 or \
            len(message.text) > 5 or len(message.text) < 4 or \
            len(splited_time[0]) < 2 or len(splited_time[1]) < 2 or \
            not splited_time[0].isdigit() or not splited_time[1].isdigit():
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f'{message.text}\nНекорректный формат! Он должен быть таким: XX:YY, где XX и YY это цифры!',
                reply_markup=cls.build_keyboard('back_to_main')
            )
            bot.register_next_step_handler(message, cls.handle_change_subtime, telegram_id=telegram_id)
        else:
            Subscription.change_notification_time(
                telegram_id=telegram_id,
                time=message.text
            )
            sub_info = Subscription.get_sub_info(telegram_id)
            sub_status = 'Включена' if sub_info['enabled'] else 'Отключена'
            sub_notify_time = sub_info['time_to_notify']
            text_message = f"Время для уведомлений было успешно изменено!\n"\
                        f"Статус подписки: {sub_status}\nВремя для уведомлений: {sub_notify_time}"
            bot.send_message(
                chat_id=message.chat.id,
                text=text_message
            )

    @classmethod
    def update(cls):
        cls.__init__()
        cls.create_schedule()

    @staticmethod
    def build_keyboard(keyboard_type):
        if keyboard_type == 'main_sub':
            keyboard = InlineKeyboardMarkup(row_width = 1)
            main_menu_button_list = [
                InlineKeyboardButton(text = 'Изменить время уведомления', callback_data = 'sub_change_time'),
                InlineKeyboardButton(text = 'Изменить параметры подписки', callback_data = 'sub_change_status'),
                InlineKeyboardButton(text = '<< Отмена', callback_data = 'sub_cancel')
            ]
            keyboard.add(*main_menu_button_list)
            return keyboard
        
        if keyboard_type == 'change_sub_actions':
            keyboard = InlineKeyboardMarkup(row_width = 1)
            main_menu_button_list = [
                InlineKeyboardButton(text = 'Включить подписку', callback_data = 'sub_enable'),
                InlineKeyboardButton(text = 'Отключить подписку', callback_data = 'sub_disable'),
                InlineKeyboardButton(text = '<< Назад', callback_data = 'sub_back_to_main')
            ]
            keyboard.add(*main_menu_button_list)
            return keyboard
        
        if keyboard_type == 'back_to_main_keyboard':
            keyboard = InlineKeyboardMarkup(row_width = 1)
            keyboard.add(InlineKeyboardButton(text = '<< Назад', callback_data = 'sub_back_to_main'))
            return keyboard