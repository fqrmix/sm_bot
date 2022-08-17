import threading
import csv
import time
import locale
import datetime
import logging
import schedule
import telebot
import config

####################
## Settings block ##
####################

# RU locale
locale.setlocale(locale.LC_ALL, '')

# Logger
logger = telebot.logger
logger.setLevel(logging.INFO)
logging.basicConfig(filename='telegram-bot.log', level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

# Telegram Bot init
bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
chatter_list_ids = []

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

def sort_by_shift(employee): 
    return employee['shift_start']

###################
## Workers block ##
###################

def create_actual_employee(current_employer, current_month, current_day):
    actual_employer_name = current_employer[current_month]
    actual_employer_info = config.employers_info[actual_employer_name]
    actual_employer_group = actual_employer_info['group']
    actual_employer_telegramid = actual_employer_info['telegram_id']

    shift_start = config.working_shift[current_employer[current_day][0]]['start']
    shift_end = config.working_shift[current_employer[current_day][0]]['end']

    actual_employer = {
        'name': actual_employer_name,
        'info': actual_employer_info,
        'group': actual_employer_group,
        'telegram_id': actual_employer_telegramid,
        'shift_start': shift_start,
        'shift_end': shift_end
    }
    return actual_employer

def create_workers_str(current_day, current_month, week_day):
    '''
        Function that create string which will be sent to Telegram Chat
        _______
        Arguments:
            *employer_list == (list) of the employers from CSV file
            *current_day == Current day from datetime() module
            *current_month == Current month with str() type
    '''
    shopmasters_list = []
    poisk_list = []
    others_list = []
    try:
        with open(config.CSV_PATH, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        for current_employer in employer_list:
            if current_employer[current_day] != '' and current_employer[current_day] != 'ОТ':

                actual_employee = create_actual_employee(current_employer, current_month, current_day)
                if actual_employee['group'] == 'ShopMaster':
                    shopmasters_list.append(actual_employee)
                elif actual_employee['group'] == 'Poisk':
                    poisk_list.append(actual_employee)
                else:
                    others_list.append(actual_employee)
            
        if week_day in range(1,6):
            with open(config.CSV_PATH_5_2, encoding = 'utf-8-sig') as csvfile:
                csv_reader = csv.DictReader(csvfile, delimiter=';')
                employer_list = list(csv_reader)
                current_day = 'Any'
                current_month = '5/2'
            for current_employer in employer_list:
                if current_employer[current_day] != '' and current_employer[current_day] != 'ОТ':
                    actual_employee = create_actual_employee(current_employer, current_month, current_day)
                    if actual_employee['group'] == 'ShopMaster':
                        shopmasters_list.append(actual_employee)
                    elif actual_employee['group'] == 'Poisk':
                        poisk_list.append(actual_employee)
                    else:
                        others_list.append(actual_employee)
        shopmasters_list.sort(key=sort_by_shift)
        poisk_list.sort(key=sort_by_shift)
        others_list.sort(key=sort_by_shift)
        return shopmasters_list, poisk_list, others_list
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

# Get list of today employers
def get_today_workers(group_list):
    '''
        Function that generate string of today employers.
        _______
        Arguments:
            *group_list == List of employees group (shopmasters_list / poisk_list / others_list)
    '''
    text_message = ''
    try:
        for employee in group_list:
            if employee['group'] == 'CMS' or employee['group'] == 'LK':
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | `{employee['group']}`" \
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
            else:
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
        return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

# Send message of today employers
def send_today_workers(chat_id, current_day, week_day, current_day_text='Сегодня работают:'):
    '''
        Function that send strings from get_today_workers() to Telegram Chat.
        _______
        Arguments:
            *chat_id == Id of Telegram Chat
    '''
    try:
        current_month = config.months[str(datetime.date.today().month)]

        shopmasters_list, poisk_list, others_list = create_workers_str(current_day, current_month, week_day)
        today_shopmasters = get_today_workers(shopmasters_list)
        today_poisk = get_today_workers(poisk_list)
        today_others = get_today_workers(others_list)
        if today_shopmasters is None or today_poisk is None or today_others is None:
            raise ValueError('Workers string is empty!')
        if week_day in range(1,6):
            text_message = f'*{current_day_text}*\n\n*Шопмастера:*\n{today_shopmasters}'\
                        f'\n*Поиск:*\n{today_poisk}\n*CMS/LK:*\n{today_others}'
        else:
            text_message = f'*{current_day_text}*\n\n*Шопмастера:*\n{today_shopmasters}'\
                        f'\n*Поиск:*\n{today_poisk}'
        bot_message = bot.send_message(
            chat_id = chat_id,
            parse_mode = 'Markdown',
            text = text_message
        )
        bot.pin_chat_message(
                chat_id=chat_id,
                message_id=bot_message.id
        )
        logger.info(f'[today-employers] Message has been successfully sent!')
    except Exception as error:
        logger.error(error, exc_info = True)

########################
## Chatter list block ##
########################

def create_chatters_str(employer_list, current_day, current_month):
    '''
        Function that create string which will be sent to Telegram Chat
        _______
        Arguments:
            *employer_list == (list) of the employers from CSV file
            *current_day == Current day from datetime() module
            *current_month == Current month with str() type
    '''
    text_message = ''
    global chatter_list_ids
    try:
        for current_employer in employer_list:
            if current_employer[current_day] != "" and current_employer[current_day] != "ОТ":
                if len(current_employer[current_day]) > 1 and current_employer[current_day][1] == "ч":
                    actual_employer_name = current_employer[current_month]
                    actual_employer_info = config.employers_info[actual_employer_name]
                    actual_employer_group = actual_employer_info['group']
                    actual_employer_telegramid = actual_employer_info['telegram_id']
                    text_message += f"[{actual_employer_name}](tg://user?id={actual_employer_telegramid})"\
                                    f" | `{actual_employer_group}`\n"
                    chatter_list_ids.append(actual_employer_telegramid)
        if chatter_list_ids == [] or text_message == '':
            err_msg = "[chatter-list] Chatters string wasn't generated (chatter_list_ids is empty)!"
            raise ValueError(err_msg)
        else:
            logger.info(f"[chatter-list] Chatters string has been successfully generated!")
            return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

def get_today_chatters(current_day):
        with open(config.CSV_PATH, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        current_month = config.months[str(datetime.date.today().month)]
        text_message = create_chatters_str(employer_list, current_day, current_month)
        return text_message

def send_chatter_list(chat_id, current_day):
    try:
        today_chatters = get_today_chatters(current_day)
        if today_chatters is None:
            raise ValueError('Chatter string is empty!')
        text_message = f"Сегодня в чатах:\n{today_chatters}"
        bot.send_message(
            chat_id=chat_id,
            parse_mode='Markdown',
            text=text_message
        )
    except Exception as error:
        logger.error(error, exc_info = True)

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
        logger.info(f'[lunch-poll] Lunch poll has been successfully sent in chatID: {chat_id}!')
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

def handle_change_subtime(message, telegram_id):
    splited_time = message.text.split(':')
    message_id=message.message_id
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


########################
##### Subscription #####
########################

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
        print(cls.get_active_subs())

    @classmethod
    def get_active_subs(cls):
        return cls.active_sub_list

    @classmethod
    def save_sub(cls):
        try:
            with open(config.JSON_DIR_PATH + 'employers_info.json', 'w', encoding='utf-8') as info_json:    
                config.json.dump(cls.employees_info, info_json, indent=4, ensure_ascii=False)
        except Exception as error:
            print(error)
        
    @classmethod
    def get_sub_info(cls, telegram_id):
        name, info = get_employer_name(
            val=str(telegram_id),
            parameter='telegram_id',
            my_dict=cls.employees_info
        )
        for employee in cls.employees_info:
            current_employee = cls.employees_info[employee]
            if employee == name:
                return current_employee['subscription']

    @classmethod
    def disable(cls, telegram_id):
        name, info = get_employer_name(
            val=str(telegram_id),
            parameter='telegram_id',
            my_dict=cls.employees_info
        )
        cls.employees_info[name]['subscription']['enabled'] = False
        cls.save_sub()
        return cls.employees_info[name]['subscription']

    @classmethod
    def enable(cls, telegram_id):
        name, info = get_employer_name(
            val=str(telegram_id),
            parameter='telegram_id',
            my_dict=cls.employees_info
        )
        cls.employees_info[name]['subscription']['enabled'] = True
        cls.save_sub()
        return cls.employees_info[name]['subscription']

    @classmethod
    def change_notification_time(cls, telegram_id, time):
        name, info = get_employer_name(
            val=str(telegram_id),
            parameter='telegram_id',
            my_dict=cls.employees_info
        )
        cls.employees_info[name]['subscription']['time_to_notify'] = time
        cls.save_sub()
        return cls.employees_info[name]['subscription']
    
    @classmethod
    def __sending_job__(cls, actual_employee):
        bot.send_message(
                chat_id = actual_employee['telegram_id'],
                parse_mode = "Markdown",
                text = f"Привет!\nТы завтра работаешь с {actual_employee['shift_start']} до {actual_employee['shift_end']}"
            )
        return schedule.CancelJob

    @classmethod
    def create_schedule(cls):
        with open(config.CSV_PATH, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        day = str(datetime.date.today().day + 1)
        current_month = config.months[str(datetime.date.today().month)]
        for current_employee_sub in cls.active_sub_list:
            for current_employee in employer_list:
                if current_employee[current_month] == current_employee_sub['name']:
                    if current_employee[day] != "" and current_employee[day] != "ОТ":
                        actual_employee = create_actual_employee(current_employee, current_month, day)
                        schedule.every().day.at(current_employee_sub['time_to_notify']).do(
                            cls.__sending_job__,
                            actual_employee=actual_employee
                        )
                        print(f"Schedule for {current_employee_sub['name']} was created, time: {current_employee_sub['time_to_notify']}")

# Initialization of Subscription class and starting schedule
Subscription().create_schedule() 

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
        message.chat.id, 
        text = text_message, 
        reply_markup = build_keyboard('main_sub')
    )

# Subscription menu callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "youtube":
        pass

    elif call.data == 'change_sub':
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
            current_day = str(datetime.date.today().day)
            week_day = datetime.date.today().isoweekday()
            send_today_workers(message.chat.id, current_day, week_day)
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
            else:
                if sign == '+':
                    past_day = str(datetime.date.today().day + int(numeric_value))
                elif sign == '-':
                    past_day = str(datetime.date.today().day - int(numeric_value))
            
            now = datetime.datetime.now()
            past_week_day = datetime.date(
                year=now.year,
                month=now.month,
                day=int(past_day)).isoweekday()

            send_today_workers(message.chat.id, past_day, week_day=past_week_day)
    except Exception as error:
        logger.error(error, exc_info = True)

# Send chatter list
@bot.message_handler(commands=['chatters'])
def handle_chatters(message):
    current_day = str(datetime.date.today().day)
    send_chatter_list(message.chat.id, current_day=current_day)

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
    global chatter_list_ids
    try:
        if str(pollAnswer.user.id) in chatter_list_ids:
            lunch_time = get_lunch_time(pollAnswer.option_ids[0])
            print(lunch_time)
            schedule.every().day.at(lunch_time).do(
                chatter_list_job,
                employer_telegram_id = pollAnswer.user.id
            )
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
    send_today_workers, 
    chat_id=config.GROUP_CHAT_ID_SM,
    current_day=current_day,
    week_day=current_week_day
)
schedule.every().day.at(TODAY_EMPOYERS_TIME).do(
    send_today_workers, 
    chat_id=config.GROUP_CHAT_ID_POISK,
    current_day=current_day,
    week_day=current_week_day
)

# Send chatters list message to SM/POISK chat groups
TODAY_CHATTERS_TIME = "08:30"
if current_week_day in range(1,6):
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        send_chatter_list, 
        chat_id=config.GROUP_CHAT_ID_SM,
        current_day=current_day,
    )
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        send_chatter_list, 
        chat_id=config.GROUP_CHAT_ID_POISK,
        current_day=current_day,
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
    current_date = datetime.date.today()
    logger.info(f'[main] Current date: {current_date}')
    if current_date.day == 1:
        logger.info('[main] Time to new CSV...\nUpdating')
        update_actual_csv(config.NEXT_MONTH_CSV_PATH, config.CSV_PATH) # Update actual CSV file
        logger.info('[main] CSV file was successfully loaded! Strarting polling!')
        stop_run_continuously = run_continuously()
        bot.infinity_polling()
        stop_run_continuously.set()
    else:
        logger.info("[main] New CSV doesn't needed! Starting polling!")
        stop_run_continuously = run_continuously()
        bot.infinity_polling()
        stop_run_continuously.set()
