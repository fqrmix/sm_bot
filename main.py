import threading
import csv
import time
import locale
import datetime
import logging
import uuid
import schedule
import telebot
import config
import caldav

####################
## Settings block ##
####################

# RU locale
locale.setlocale(locale.LC_ALL, '')

# Logger
logger = telebot.logger
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
file_handler = logging.FileHandler('telegram-bot.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

trace_logger = logging.getLogger('logger')
trace_logger .setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - [%(trace_id)s] - %(message)s')
file_handler = logging.FileHandler('telegram-bot.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
trace_logger.addHandler(file_handler)


################################################
################# Classes Block ################
################################################

########################
##### Subscription #####
########################

class Subscription:
    @classmethod
    def __init__(cls):
        current_employee_sub = {}
        cls.active_sub_list = []
        cls.employees_info = config.employers_info
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
            with open(config.JSON_DIR_PATH + 'employers_info.json', 'w', encoding='utf-8') as info_json:    
                config.json.dump(cls.employees_info, info_json, indent=4, ensure_ascii=False)
            logger.info(msg="[sub] Subscription JSON info was dumped to server")
        except Exception as error:
            logger.error(error, exc_info = True)
        
    @classmethod
    def get_sub_info(cls, telegram_id):
        try:
            name, info = get_employer_name(
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
            name, info = get_employer_name(
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
            name, info = get_employer_name(
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
            name, info = get_employer_name(
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
                    text = f"Привет!\nТы завтра работаешь с {actual_employee['shift_start']} до {actual_employee['shift_end']}"
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
    def create_schedule(cls):
        try:
            all_employees = Employees()
            day = str(datetime.date.today().day + 1)
            for current_employee_sub in cls.active_sub_list:
                for current_employee in all_employees.employees:
                    if current_employee['name'] == current_employee_sub['name']:
                        if current_employee['shifts'][day] != "" \
                        and current_employee['shifts'][day] != "ОТ":
                            actual_employee = DayWorkers.create_actual_employee(current_employee, day)
                            schedule.every().day.at(current_employee_sub['time_to_notify']).do(
                                cls.__sending_job__,
                                actual_employee=actual_employee
                            )
                            logger.info(
                                msg=f"[Sub] Schedule for {current_employee_sub['name']} was created," \
                                    f" time: {current_employee_sub['time_to_notify']}")
        except Exception as error:
            logger.error(error, exc_info = True)
def handle_change_subtime(message, telegram_id):
    splited_time = message.text.split(':')
    if len(splited_time) < 2 or \
        len(message.text) > 5 or len(message.text) < 4 or \
        len(splited_time[0]) < 2 or len(splited_time[1]) < 2 or \
        not splited_time[0].isdigit() or not splited_time[1].isdigit():
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=f'{message.text}\nНекорректный формат! Он должен быть таким: XX:YY, где XX и YY это цифры!',
            reply_markup=build_keyboard('back_to_main')
        )
        bot.register_next_step_handler(message, handle_change_subtime, telegram_id=telegram_id)
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

def build_keyboard(keyboard_type):
    if keyboard_type == 'main_sub':
        keyboard = telebot.types.InlineKeyboardMarkup(row_width = 1)
        main_menu_button_list = [
            telebot.types.InlineKeyboardButton(text = 'Изменить время уведомления', callback_data = 'change_time'),
            telebot.types.InlineKeyboardButton(text = 'Изменить параметры подписки', callback_data = 'change_sub'),
        ]
        keyboard.add(*main_menu_button_list)
        return keyboard
    
    if keyboard_type == 'change_sub_actions':
        keyboard = telebot.types.InlineKeyboardMarkup(row_width = 1)
        main_menu_button_list = [
            telebot.types.InlineKeyboardButton(text = 'Включить подписку', callback_data = 'enable_sub'),
            telebot.types.InlineKeyboardButton(text = 'Отключить подписку', callback_data = 'disable_sub'),
            telebot.types.InlineKeyboardButton(text = '<< Назад', callback_data = 'back_to_main')
        ]
        keyboard.add(*main_menu_button_list)
        return keyboard
    
    if keyboard_type == 'back_to_main_keyboard':
        keyboard = telebot.types.InlineKeyboardMarkup(row_width = 1)
        keyboard.add(telebot.types.InlineKeyboardButton(text = '<< Get back', callback_data = 'back_to_main'))
        return keyboard


###########################
#####  WebDAV block  ######
###########################

class Client:
    def __init__(self, login, password) -> None:
        webdav_url = 'https://webdav.fqrmix.ru'
        self.current_client = caldav.DAVClient(
            url=webdav_url,
            username=login,
            password=password
        )
        self.current_principle = self.current_client.principal()
        logger.info(f"[WebDAV] Connected by login: {login}")
        try:
            self.work_calendar = self.current_principle.calendar(name="Work")
            assert self.work_calendar
            self.work_calendar_url = self.work_calendar.url
            assert self.work_calendar_url
            logger.info(f"[WebDAV] Found Work calendar for login: {login}")
        except caldav.error.NotFoundError:
            logger.info(f"[WebDAV] Work calendar wasn't found for login: {login}. Creating calendar...")
            self.work_calendar = self.current_principle.make_calendar(name="Work")
            self.work_calendar_url = self.work_calendar.url
            assert self.work_calendar_url
            logger.info(f"[WebDAV] Work calendar was successfuly created for login: {login}")
            

    def get_calendars(self):
        calendars = self.current_principle.calendars()
        current_calendars = []
        current_calendar = {}
        if calendars:
            for c in calendars:
                current_calendar['name'] = c.name
                current_calendar['url'] = c.url
                current_calendars.append(current_calendar)
            return current_calendars
        else:
            return None

    def create_event(self, date_start, date_end, summary, month, time_start, time_end):
        try:
            event = self.work_calendar.save_event(
                dtstart=datetime.datetime(2022, month, date_start, time_start),
                dtend=datetime.datetime(2022, month, date_end, time_end),
                summary=summary
            )
        except Exception as error:
            logger.error(error, exc_info=True)

    def get_events(self, calendar_name):
        result = self.current_principle.calendar(name=calendar_name).events()
        if result == []:
            return None
        else:
            return result
    
    def delete_all_events(self, calendar_name):
        try:
            all_events = self.get_events(calendar_name=calendar_name)
            if all_events:
                for event in all_events:
                    event.delete()
            else:
                print('Calendar is empty!')
        except Exception as error:
            logger.error(error, exc_info=True)


class WebDAV:
    def __init__(self, path=None) -> None:
        if path is not None:
            self.employee_list = self.get_employee_list(path)
        else:
            self.employee_list = self.get_employee_list(config.CSV_PATH)
        self.employeеs_info = config.employers_info
    
    def get_webdav_info(self, telegram_id):
        try:
            webdav_info = {}
            for employee in self.employeеs_info:
                current_employee = self.employeеs_info[employee]
                if current_employee['telegram_id'] == telegram_id:
                    webdav_info['name'] = current_employee['webdav']['name']
                    webdav_info['url'] = current_employee['webdav']['url']
                    webdav_info['login'] = current_employee['telegram']
                    webdav_info['password'] = current_employee['webdav']['password']
            return webdav_info
        except Exception as error:
            logger.error(error, exc_info=True)

    def save_info(self):
        try:
            with open(config.JSON_DIR_PATH + 'employers_info.json', 'w', encoding='utf-8') as info_json:    
                config.json.dump(self.employeеs_info, info_json, indent=4, ensure_ascii=False)
        except Exception as error:
            logger.error(error, exc_info=True)
    
    def generate_calendar(self, month):
        try:
            for c_w in self.employee_list:
                current_employee_name = c_w[config.months[str(month)]]
                print(current_employee_name)
                current_employee_info = self.employeеs_info[current_employee_name]
                actual_employee_login = current_employee_info['telegram']
                actual_employee_password = current_employee_info['webdav']['password']
                current_client = Client(actual_employee_login, actual_employee_password)
                vacation_flag = False
                vacation_day_start = 0
                vacation_day_end = 0
                for item in c_w:
                    if c_w[item] != '' and c_w[item] != 'ОТ' and c_w[item] != current_employee_name:
                        shift_start = config.working_shift[c_w[item][0]]['start'].split(':')
                        shift_end = config.working_shift[c_w[item][0]]['end'].split(':')
                        int_shift_start = int(shift_start[0])
                        int_shift_end = int(shift_end[0])
                        int_day_start = int(item)
                        int_day_end = int(item)
                        print(f"День: {item}\nСмена: {int(shift_start[0])} - {int(shift_end[0])}\n")
                        if int_shift_start == 12 and int_shift_end == 0:
                            int_day_end = int(item) + 1
                        current_client.create_event(
                            date_start=int_day_start,
                            date_end=int_day_end,
                            month=month,
                            time_start=int_shift_start,
                            time_end=int_shift_end,
                            summary='Смена'
                        )
                        logger.info(f'[WebDAV] [{current_employee_name}] Created event for {item} of {config.months[str(month)]}')

                    if c_w[item] == 'ОТ' and c_w[item] != current_employee_name:
                        if not vacation_flag:
                            vacation_flag = True
                            vacation_day_start = int(item)
                            vacation_day_end = vacation_day_start
                        else:
                            vacation_day_end = int(item)
                    if c_w[item] != 'ОТ' and vacation_flag and c_w[item] != current_employee_name:
                        vacation_flag = False
                if vacation_day_start > 0 and vacation_day_end > 0:
                    current_client.create_event(
                                date_start=vacation_day_start,
                                date_end=vacation_day_end,
                                month=month,
                                time_start=0,
                                time_end=12,
                                summary='Отпуск'
                            )
                self.employeеs_info[current_employee_name]['webdav']['url'] = str(current_client.work_calendar_url)
                self.save_info()
        except Exception as error:
            logger.error(error, exc_info=True)
                        

    @staticmethod
    def get_employee_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employee_list = list(csv_reader)
        return employee_list

###################
## Workers block ##
###################

class Employees:
    def __init__(self) -> None:
        employees_list = self.get_employer_list(config.CSV_PATH)
        fulltime_employees_list = self.get_employer_list(config.CSV_PATH_5_2)
        self.employees = []
        self.fulltime_employees = []
        actual_employee = {
            'name': '',
            'shifts': {}
        }

        # Creating 2/2 employees list
        for employee in employees_list:
            for current_employee in employee:
                if len(employee[current_employee]) > 2:
                    actual_employee['name'] = employee[current_employee]
                else:
                    actual_employee['shifts'][current_employee] = employee[current_employee]
            self.employees.append(actual_employee)
            actual_employee = {
                'name': '',
                'shifts': {}
            }
        
        # Creating 5/2 employess list
        for employee in fulltime_employees_list:
            actual_employee['name'] = employee['5/2']
            actual_employee['shifts']['Any'] = employee['Any']
            self.fulltime_employees.append(actual_employee)
            actual_employee = {
                'name': '',
                'shifts': {}
            }  

    @staticmethod
    def get_employer_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        return employer_list


class DayWorkers(Employees):
    def __init__(self, current_day=None) -> None:
        super().__init__()
        if current_day is None:
            self.current_day = str(datetime.date.today().day)
            self.week_day = datetime.date.today().isoweekday()
        else:
            self.current_day = current_day
            now = datetime.datetime.now()
            past_week_day = datetime.date(
                year=now.year,
                month=now.month,
                day=int(current_day)).isoweekday()
            self.week_day = past_week_day
        
        self.workers_list = []

        for current_employer in self.employees:
            if current_employer['shifts'][self.current_day] != '' \
            and current_employer['shifts'][self.current_day] != 'ОТ':
                actual_employee = self.create_actual_employee(
                    current_employer, 
                    self.current_day
                    )
                if len(current_employer['shifts'][self.current_day]) > 1 \
                and current_employer['shifts'][self.current_day][1] == "ч":
                    actual_employee['chat']['state'] = True
                self.workers_list.append(actual_employee)

        if self.week_day in range(1,6):
            for current_employer in self.fulltime_employees:
                if current_employer['shifts']['Any'] != '' \
                and current_employer['shifts']['Any'] != 'ОТ':
                    actual_employee = self.create_actual_employee(
                        current_employer, 
                        'Any'
                        )
                    self.workers_list.append(actual_employee)

    def split_by_group(self) -> list:
        shopmasters_list = []
        poisk_list = []
        others_list = []
        for current_employer in self.workers_list:
            if current_employer['group'] == 'ShopMaster':
                shopmasters_list.append(current_employer)
            elif current_employer['group'] == 'Poisk':
                poisk_list.append(current_employer)
            else:
                others_list.append(current_employer)
        shopmasters_list.sort(key=self.sort_by_shift)
        poisk_list.sort(key=self.sort_by_shift)
        others_list.sort(key=self.sort_by_shift)
        return shopmasters_list, poisk_list, others_list

    def send_message(self, chat_id, current_day_text='Сегодня работают:') -> str:
        shopmasters_list, poisk_list, others_list = self.split_by_group()
        current_day_sm = self.create_str(shopmasters_list) 
        current_day_sm_text = f'*Шопмастера:*\n{current_day_sm}'\
            if shopmasters_list != [] else ''
        current_day_poisk = self.create_str(poisk_list)
        current_day_poisk_text = f'*Поиск:*\n{current_day_poisk}'\
            if poisk_list != [] else ''
        current_day_others = self.create_str(others_list)
        current_day_others_text = f'*CMS/LK:*\n{current_day_others}'\
            if others_list != [] else ''
        text_message = f'*{current_day_text}*\n\n{current_day_sm_text}\n'\
                        f'{current_day_poisk_text}\n'\
                        f'{current_day_others_text}'
        bot_message = bot.send_message(
            chat_id = chat_id,
            parse_mode = 'Markdown',
            text = text_message
        )
        if current_day_text == 'Сегодня работают:':
            bot.pin_chat_message(
                    chat_id=chat_id,
                    message_id=bot_message.id
            )

    """
    Workers class static methods
    """

    @staticmethod
    def get_employer_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        return employer_list

    @staticmethod
    def sort_by_shift(employee): 
        return employee['shift_start']

    @staticmethod
    def create_actual_employee(current_employer, current_day):
        actual_employee_name = current_employer['name']
        actual_employee_info = config.employers_info[actual_employee_name]
        actual_employee_group = actual_employee_info['group']
        actual_employee_telegramid = actual_employee_info['telegram_id']

        shift_start = config.working_shift[current_employer['shifts'][current_day][0]]['start']
        shift_end = config.working_shift[current_employer['shifts'][current_day][0]]['end']

        actual_employee = {
            'name': actual_employee_name,
            'group': actual_employee_group,
            'telegram_id': actual_employee_telegramid,
            'shift_start': shift_start,
            'shift_end': shift_end,
            'chat': {
                'state': False,
                'lunch_time': None,
                'scheduled': False
            }
        }
        return actual_employee
    
    @staticmethod
    def create_str(group_list):
        text_message = ''
        for employee in group_list:
            if employee['group'] == 'CMS' or employee['group'] == 'LK':
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | `{employee['group']}`" \
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
            else:
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
        return text_message


########################
## Chatter list block ##
########################

class Chatters(DayWorkers):
    def __init__(self) -> None:
        super().__init__()
        self.chatter_list = []
        for current_emoloyer in self.workers_list:
            if current_emoloyer['chat']['state']:
                self.chatter_list.append(current_emoloyer)
    
    def print_list(self):
        for chatter in self.chatter_list:
            print(chatter)
    
    def create_chatters_str(self):
        text_message = ''
        for current_chatter in self.chatter_list:
            actual_employer_name = current_chatter['name']
            actual_employer_group = current_chatter['group']
            actual_employer_telegramid = current_chatter['telegram_id']
            text_message += f"[{actual_employer_name}](tg://user?id={actual_employer_telegramid})"\
                            f" | `{actual_employer_group}`\n"
        return text_message

    def send_chatter_list(self, chat_id):
        try:
            today_chatters = self.create_chatters_str()
            text_message = f"Сегодня в чатах:\n{today_chatters}"
            bot.send_message(
                chat_id=chat_id,
                parse_mode='Markdown',
                text=text_message
            )
            logger.info(f"[chatter-list] Chatter string was successfully sent into chatID: {chat_id}")
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def build_chatter_keyboard(self):
        chattter_menu_button_list = []
        keyboard = telebot.types.InlineKeyboardMarkup(row_width = 2)
        for current_employee in self.workers_list:
            if not current_employee['chat']['state']:
                button = telebot.types.InlineKeyboardButton(
                    text = current_employee['name'], 
                    callback_data = 'chatter_' + current_employee['telegram_id'])
                chattter_menu_button_list.append(button)
        back_button = telebot.types.InlineKeyboardButton(
                    text = 'Назад', 
                    callback_data = 'cancel')
        chattter_menu_button_list.append(back_button)
        keyboard.add(*chattter_menu_button_list)
        return keyboard
    
    def add_chatter_message(self, message):
        try:
            today_chatters = self.create_chatters_str()
            text_message = f"Сейчас в чатах:\n{today_chatters}\n"\
                f"Выбери сотрудника для добавления:\n"
            markup_keyboard = self.build_chatter_keyboard()
            bot.send_message(
                chat_id=message.chat.id,
                text=text_message,
                parse_mode='Markdown',
                reply_markup=markup_keyboard
            )
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def add_chatter(self, telegram_id):
        chat_id = ''
        text_message = ''
        for current_emoloyer in self.workers_list:
            if current_emoloyer['telegram_id'] == telegram_id:
                self.chatter_list.append(current_emoloyer)
                if current_emoloyer['group'] == 'Poisk':
                    chat_id = config.GROUP_CHAT_ID_POISK
                else:
                    chat_id = config.GROUP_CHAT_ID_SM
                text_message = f"[{current_emoloyer['name']}](tg://user?id={current_emoloyer['telegram_id']}), "\
                    f"привет! Заходи, пожалуйста, в чаты."
                message = bot.send_message(
                    chat_id=chat_id,
                    text=text_message,
                    parse_mode='Markdown'
                )
                return message


#####################
## Basic functions ##
#####################

# Updating CSV file
def update_actual_csv(nextpath, path):
    '''
        Function that update actual CSV file with CSV file for next month
        _______
        Arguments:
            *nextpath == Path to CSV file for next month
            *path == Path to actual CSV file
    '''
    try:
        with open(path, 'w+', encoding='utf-8') as write_file:
            with open(nextpath, 'r', encoding='utf-8') as read_file:
                data = read_file.read()
                write_file.write(data)
            logger.info("[load] The schedule for next month has been successfully updated!")
    except Exception as error_msg:
        logger.error(error_msg, exc_info=True)

# Get employer name
def get_employer_name(val: str, parameter: str, my_dict: dict):
    '''
        Function that return employer name by paramater.
        If paramater doesn't exists in my_dict - return None instead.
        _______
        Arguments:
            *val == Parameter which searched
            *parametr == Search parameter
            *my_dict == Dict
    '''
    for key, value in my_dict.items():
        if val == value[parameter]:
            return key, value
    return None, None

# Get log n str
def get_log_str(log_name, lines):
    with open(log_name, encoding='utf-8') as file:
        result = ''
        for line in (file.readlines()[-lines:]):
            result += line
    return result


def get_notification_time(str):
    new_str = str.split(':')
    time_hour = int(new_str[0]) - 1
    time_minutes = int(new_str[1]) + 55
    return f'{time_hour}:{time_minutes}'


def get_lunch_time(option_id):
    options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00']
    lunch_time = options[option_id]
    return get_notification_time(lunch_time)


########################
##  Lunch poll block  ##
########################

# Send lunch poll
def send_lunch_query(chat_id):
    '''
        Function that send lunch poll to Telegram Chat.
        _______
        Arguments:
            *chat_id == Id of Telegram Chat
    '''
    try:
        bot.send_poll(
            chat_id = chat_id,
            question = 'Доброе утро!\nВо сколько обед?',
            is_anonymous = False,
            options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'])
        logger.info(f'[lunch-poll] Lunch poll has been successfully sent into chatID: {chat_id}!')
    except Exception as error:
        logger.error(error, exc_info = True)

# Chatter list job
def chatter_list_job(employer_telegram_id):
    try:
        chat_id = None
        employer_name, employer_info = get_employer_name(
            val=str(employer_telegram_id),
            parameter='telegram_id', 
            my_dict=config.employers_info
        )
        print(employer_info)
        if employer_info['group'] == 'ShopMaster':
            chat_id = config.GROUP_CHAT_ID_SM
            pass
        elif employer_info['group'] == 'Poisk':
            chat_id = config.GROUP_CHAT_ID_POISK
        if chat_id is not None:
            bot.send_message(
                chat_id = chat_id,
                parse_mode = "Markdown",
                text = f"[{employer_name}](tg://user?id={employer_telegram_id}) скоро уйдет на обед."\
                    f"\nКоллеги, подмените пожалуйста его в чатах."
            )
            return schedule.CancelJob
        else:
            return schedule.CancelJob
    except Exception as error:
        logger.error(error, exc_info = True)

###########################
## Initialization block ###
###########################

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
today_workers = DayWorkers()
today_chatters = Chatters()
Subscription().create_schedule()
chatter_list = []

###########################
## Telegram Bot Handlers ##
###########################

# Init
@bot.message_handler(commands=['init'])
def init_bot(message):
    '''
        Telegram handler of command /init, which init bot in some chat.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        bot.send_message(
                chat_id = message.chat.id,
                parse_mode = 'Markdown',
                text = f'Init in chat group:\nID: {message.chat.id}\nChat name: {message.chat.title}'
            )
        logger.info(f"[init] Initialization was completed in chatID - {message.chat.id}, "\
            f"chatName - {message.chat.title}, by user - @{message.from_user.username}")
    except Exception as error:
        logger.error(error, exc_info = True)

# WebDAV menu
@bot.message_handler(commands=['webdav'])
def web_dav_menu(message):
    telegram_id = message.from_user.id
    webdav_info = WebDAV().get_webdav_info(str(telegram_id))
    text_message = f"*Название календаря:* `{webdav_info['name']}`\n"\
                    f"*URL календаря:* {webdav_info['url']}\n\n*Информация для подключения к серверу:*\n\n"\
                    f"*Адрес:* https://webdav.fqrmix.ru\n*Логин:* `{webdav_info['login']}`\n*Пароль:* `{webdav_info['password']}`"
    bot.send_message(
        chat_id=message.chat.id,
        text=text_message,
        parse_mode='markdown'
    )

# Subscription menu
@bot.message_handler(commands=['subscription', 'sub'])
def sub_menu(message):
    telegram_id = message.from_user.id
    sub_info = Subscription.get_sub_info(telegram_id)
    sub_status = 'Включена' if sub_info['enabled'] else 'Отключена'
    sub_notify_time = sub_info['time_to_notify']
    text_message = f"Статус подписки: {sub_status}\nВремя для уведомлений: {sub_notify_time}" if sub_info['enabled'] else \
                    f"Статус подписки: {sub_status}"
    bot.send_message(
        chat_id=message.chat.id, 
        text=text_message, 
        reply_markup=build_keyboard('main_sub')
    )

# Subscription menu callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(call.data)
    if call.data == 'change_sub':
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = 'Выбери действие [Включить/Отключить]', 
            reply_markup = build_keyboard('change_sub_actions'))
    
    elif call.data == 'enable_sub':
        telegram_id = call.from_user.id
        sub_info = Subscription.get_sub_info(telegram_id)
        if sub_info['enabled']:
            bot.send_message(
                chat_id=call.message.chat.id,
                text='Подписка уже активна!'
            )
        else:
            Subscription.enable(telegram_id)
            bot.send_message(
                chat_id=call.message.chat.id,
                text='Подписка была успешно включена!'
            )

    elif call.data == 'disable_sub':
        telegram_id = call.from_user.id
        sub_info = Subscription.get_sub_info(telegram_id)
        if not sub_info['enabled']:
            bot.send_message(
                chat_id=call.message.chat.id,
                text='Подписка уже отключена!'
            )
        else:
            Subscription.disable(telegram_id)
            bot.send_message(
                chat_id=call.message.chat.id,
                text='Подписка была успешно отключена!'
            )
    
    elif call.data == 'change_time':
        telegram_id = call.from_user.id
        sub_info = Subscription.get_sub_info(telegram_id)
        if not sub_info['enabled']:
            bot.send_message(
                chat_id=call.message.chat.id,
                text='Подписка отключена!'\
                    'Необходимо ее включить для редактирования времени уведомления!'
            )
        else:
            inner_message = bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text='Пришли мне время в формате XX:YY',
                reply_markup=build_keyboard('back_to_main_keyboard')
            )
            bot.register_next_step_handler(inner_message, handle_change_subtime, telegram_id=telegram_id)

    elif call.data == 'back_to_main':
        bot.clear_step_handler(call.message)
        telegram_id = call.from_user.id
        sub_info = Subscription.get_sub_info(telegram_id)
        sub_status = 'Включена' if sub_info['enabled'] else 'Отключена'
        sub_notify_time = sub_info['time_to_notify']
        text_message = f"Статус подписки: {sub_status}\nВремя для уведомлений: {sub_notify_time}" if sub_info['enabled'] else \
                        f"Статус подписки: {sub_status}"
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = text_message, 
            reply_markup = build_keyboard('main_sub')
        )
    elif call.data.startswith('chatter_'):
        telegram_id = call.data.replace('chatter_', '')
        Chatters().add_chatter(telegram_id)
        bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = 'Готово, сообщение для сотрудника отправлено в соответствующий чат!', 
            reply_markup = '')

# Loading .csv file
@bot.message_handler(commands=['load'])
def handle_loader(message):
    '''
        Telegram handler of command /load, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    employer_name, value = get_employer_name(
        val = message.from_user.username,
        parameter = "telegram",
        my_dict = config.employers_info)
    if employer_name is None:
        bot.send_message(
            chat_id = message.chat.id,
            text = "Данная команда предназначена только для сотрудников тех. сопровождения/подключения!")
        error_msg = f"[load] User @{message.from_user.username} use command /load in chatID "\
            f"- {message.chat.id}, chatName - {message.chat.title}, but he doesn't exist in employers database!"
        raise ValueError(error_msg)
    else:
        logger.info(f'[load] User "{message.from_user.username}" trying to load a new CSV file')
        link_message = bot.send_message(
                    chat_id = message.chat.id,
                    text = 'Пришли мне файл с графиком в формате .CSV на следующий месяц')
        bot.register_next_step_handler(link_message, load_employers_csv)

def load_employers_csv(message):
    '''
        Continiuous function of load handler.
    '''
    if message.content_type != 'document':
        if message.text == "/cancel":
            bot.send_message(message.chat.id, "Loading was canceled by user")
            logger.info(f"[load] Loading was canceled by user @{message.from_user.username}")
        else:
            bot.send_message(message.chat.id, f"I am waiting for CSV file!\n"\
                f"Not for {message.content_type}!\nUse /cancel command to quit")
            bot.register_next_step_handler(message, load_employers_csv)
    else:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(config.NEXT_MONTH_CSV_PATH, 'wb') as csv_file:
                csv_file.write(downloaded_file)
            bot.reply_to(message, "График на следующий месяц загружен!")
            logger.info("[load] График на следующий месяц загружен!")
            current_month = datetime.date.today().month
            next_month = current_month + 1 if current_month != 12 else 1
            WebDAV(config.NEXT_MONTH_CSV_PATH).generate_calendar(month=next_month)
        except Exception as error:
            logger.error(error, exc_info = True)

# Get list of today employers
@bot.message_handler(commands=['workers'])
def handle_workers(message):
    '''
        Telegram handler of command /workers, which send list of today workers.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        if len(message.text) == 8 or len(message.text) == 22: # If message.text contains nothing but /workers or /workers@fqrmix_sm_bot command
            today_workers.send_message(message.chat.id)
        else:
            sign = ''
            numeric_value = ''
            if len(message.text) > 22:
                value = (message.text).replace('/workers@fqrmix_sm_bot ', '') # Value after /workers command
            else:
                value = (message.text).replace('/workers ', '') # Value after /workers command

            if value.startswith('+'):
                sign = '+'
                numeric_value = value.replace('+', '')
            elif value.startswith('-'):
                sign = '-'
                numeric_value = value.replace('-', '')

            if (not numeric_value.isdigit() and sign != '') or \
                (not value.isdigit() and sign == ''):
                err_msg = 'Only digits allowed to use after /workers command!\nUse:\n\n'\
                    '[/workers +1] - Get list of tommorow workers\n'\
                    '[/workers -1] - Get list of yesterday workers\n'\
                    '[/workers 23] - Get workers which works at 23 day of current month'
                raise ValueError(err_msg)
            if sign == '' and numeric_value == '':
                past_day = value
                day_str = f"Работающие {past_day} числа текущего месяца:"
            else:
                if sign == '+':
                    past_day = str(datetime.date.today().day + int(numeric_value))
                    day_str = f"{past_day} числа текущего месяца будут работать:"
                elif sign == '-':
                    past_day = str(datetime.date.today().day - int(numeric_value))
                    day_str = f"{past_day} числа текущего месяца работали:"
            anyday_workers = DayWorkers(current_day=past_day)
            anyday_workers.send_message(
                chat_id = message.chat.id,
                current_day_text= day_str
                )
    except Exception as error:
        logger.error(error, exc_info = True)

# Send chatters list
@bot.message_handler(commands=['chatters'])
def handle_chatters(message):
    Chatters().send_chatter_list(message.chat.id)

# Add chatter to list
@bot.message_handler(commands=['addchatter'])
def handle_chatters(message):
    Chatters().add_chatter_message(message)

# Repeat lunch poll
@bot.message_handler(commands=['lunch'])
def handle_lunch(message):
    '''
        Telegram handler of command /lunch, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    send_lunch_query(message.chat.id)

# Out for lunch
@bot.message_handler(commands=['out'])
def handle_out(message):
    '''
        Telegram handler of command /out, which send notification about employers goes for lunch,
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        employer_telegram_id = message.from_user.id
        employer_name, value = get_employer_name(
            val = str(employer_telegram_id),
            parameter = 'telegram_id',
            my_dict = config.employers_info)
        print(employer_name)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для сотрудников тех. сопровождения/подключения!")
            error_msg = f"[out] User @{message.from_user.username} use command /out in chatID - {message.chat.id}, "\
                f"chatName - {message.chat.title}, but he doesn't exist in employers database!"
            raise ValueError(error_msg)
        bot.send_message(
            chat_id = message.chat.id,
            parse_mode = "Markdown",
            text = f"[{employer_name}](tg://user?id={employer_telegram_id}) ушел(-ла) на обед."\
                f"\nКоллеги, подмените пожалуйста его в чатах.")
        logger.info(f"[out] User @{message.from_user.username} successfully use command /out in "\
            f"chatID - {message.chat.id}, chatName - {message.chat.title}")
    except Exception as error:
        logger.error(error, exc_info = True)

# Auto-out for lunch
@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    if len(pollAnswer.option_ids) > 0:
        lunch_time = get_lunch_time(pollAnswer.option_ids[0])
        logger.info(f'[poll-answer-handler] User {pollAnswer.user.id} has choosen {lunch_time} time for lunch')
        try:
            for current_chatter in today_chatters.chatter_list:
                if current_chatter['telegram_id'] == str(pollAnswer.user.id):
                    logger.info(f"[poll-answer-handler] User {pollAnswer.user.id} was found in chatter list\n"\
                        f"Subject: {today_chatters.chatter_list}")
                    if current_chatter['chat']['scheduled']:
                        logger.info(f'[poll-answer-handler] Schedule for user {pollAnswer.user.id} was already created')
                        schedule.clear(str(pollAnswer.user.id))
                        logger.info(f'[poll-answer-handler] Previous schedule for user {pollAnswer.user.id} was removed')
                    schedule.every().day.at(lunch_time).do(
                        chatter_list_job,
                        employer_telegram_id = pollAnswer.user.id
                    ).tag(str(pollAnswer.user.id))
                    logger.info(f'[poll-answer-handler] Schedule for lunch-out was created for user {pollAnswer.user.id}')
                    current_chatter['chat']['lunch_time'] = lunch_time
                    current_chatter['chat']['scheduled'] = True
                    logger.info(f"[poll-answer-handler] User {pollAnswer.user.id} "\
                        f"lunch time: {current_chatter['chat']['lunch_time']}, "\
                        f"schedule status: {current_chatter['chat']['scheduled']}")
                    print(schedule.get_jobs(str(pollAnswer.user.id)))
        except Exception as error:
            logger.error(error, exc_info = True)

# Get log into chat
@bot.message_handler(commands=['log'])
def handle_log(message):
    '''
        Telegram handler of command /log, which send log file into chat.
        _______
        Arguments:
            *message == Object of message
    '''
    value = (message.text).replace('/log ', '') # Number after /log message
    lines = 5 if value == '/log' else int(value) # 5 - default value, if value in message is empty
    log_to_bot = get_log_str(log_name='telegram-bot.log', lines=lines)
    try:
        if len(log_to_bot) > 4096:
            for x in range(0, len(log_to_bot), 4096):
                bot.send_message(
                    chat_id = message.chat.id,
                    parse_mode='Markdown',
                    text = f'`{log_to_bot[x:x+4096]}`')
        else:
            bot.send_message(
                chat_id = message.chat.id,
                parse_mode='Markdown',
                text = f'`{log_to_bot}`')
    except Exception as error:
        logger.error(error, exc_info = True)
        bot.reply_to(message, text=error)

########################
####### Sсhedule #######
########################

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

current_day = str(datetime.date.today().day)
current_week_day = datetime.date.today().isoweekday()

# Send today employers message to SM/POISK chat groups
TODAY_EMPOYERS_TIME = "08:00"
schedule.every().day.at(TODAY_EMPOYERS_TIME).do(
    today_workers.send_message, 
    chat_id=config.GROUP_CHAT_ID_SM
)
schedule.every().day.at(TODAY_EMPOYERS_TIME).do(
    today_workers.send_message, 
    chat_id=config.GROUP_CHAT_ID_POISK,
    current_day=current_day,
    week_day=current_week_day
)

# Send chatters list message to SM/POISK chat groups
TODAY_CHATTERS_TIME = "08:30"
if current_week_day in range(1,6):
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        today_chatters.send_chatter_list, 
        chat_id=config.GROUP_CHAT_ID_SM,
    )
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        today_chatters.send_chatter_list, 
        chat_id=config.GROUP_CHAT_ID_POISK,
    )

# Send today lunch-poll message to SM/POISK chat groups
TODAY_LUNCH_TIME = "10:00"
schedule.every().day.at(TODAY_LUNCH_TIME).do(
    send_lunch_query,
    chat_id=config.GROUP_CHAT_ID_SM
)
schedule.every().day.at(TODAY_LUNCH_TIME).do(
    send_lunch_query, 
    chat_id=config.GROUP_CHAT_ID_POISK
)


############################
## Start infinity polling ##
############################

if __name__ == '__main__':
    logger_data = {
            'trace_id': uuid.uuid4()
        }
    current_date = datetime.date.today()
    trace_logger.info(f'[main] Current date: {current_date}', extra=logger_data)
    if current_date.day == 1:
        trace_logger.info('[main] Time to new CSV...\nUpdating')
        update_actual_csv(config.NEXT_MONTH_CSV_PATH, config.CSV_PATH) # Update actual CSV file
        trace_logger.info('[main] CSV file was successfully loaded! Strarting polling!', extra=logger_data)
        stop_run_continuously = run_continuously()
        bot.infinity_polling()
        stop_run_continuously.set()
    else:
        trace_logger.info("[main] New CSV doesn't needed! Starting polling!", extra=logger_data)
        stop_run_continuously = run_continuously()
        bot.infinity_polling()
        stop_run_continuously.set()
        