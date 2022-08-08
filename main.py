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

def get_lunch_time(option_id):
    options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00']
    return str(options[option_id])

###################
## Workers block ##
###################

def create_workers_str(employer_list, current_day, current_month):
    '''
        Function that create string which will be sent to Telegram Chat
        _______
        Arguments:
            *employer_list == (list) of the employers from CSV file
            *current_day == Current day from datetime() module
            *current_month == Current month with str() type
    '''
    text_message = ''
    try:
        for current_employer in employer_list:
            if current_employer[current_day] != '' and current_employer[current_day] != 'ОТ':
                # If current employer works today and don't at vacation
                actual_employer_name = current_employer[current_month]
                actual_employer_info = config.employers_info[actual_employer_name]
                actual_employer_group = actual_employer_info['group']
                actual_employer_telegramid = actual_employer_info['telegram_id']

                shift_start = config.working_shift[current_employer[current_day][0]]['start']
                shift_end = config.working_shift[current_employer[current_day][0]]['end']

                text_message += f"[{actual_employer_name}](tg://user?id={actual_employer_telegramid})"\
                f" | `{actual_employer_group}`" \
                f" | Cмена: `{shift_start}` - `{shift_end}`\n"

        logger.info(f"[today-employers] Employers string has been successfully generated!")
        return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

# Get list of today employers
def get_today_workers(path, current_day, shift="2/2", chat=False):
    '''
        Function that generate string of today employers.
        _______
        Arguments:
            *path == Path to actual CSV file
            *shift == Working shift (can be used as "2/2" or "5/2")
    '''
    try:
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
            if shift == "5/2":
                current_month = "5/2"
                current_day = "Any"
            else:
                current_month = config.months[str(datetime.date.today().month)]
            if not chat:
                text_message = create_workers_str(employer_list, current_day, current_month)
            else:
                text_message = create_chatters_str(employer_list, current_day, current_month)
            return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

# Send message of today employers
def send_today_workers(chat_id, current_day, week_day):
    '''
        Function that send strings from get_today_workers() to Telegram Chat.
        _______
        Arguments:
            *chat_id == Id of Telegram Chat
    '''
    try:
        if week_day in range(1,6):
            today_2_2_employers = get_today_workers(
                path=config.CSV_PATH,
                current_day=current_day,
                shift="2/2",
                chat=False
            )
            today_5_2_employers = get_today_workers(
                path=config.CSV_PATH_5_2, 
                current_day=current_day, 
                shift="5/2", 
                chat=False
            )
            if today_2_2_employers is None or today_5_2_employers is None:
                raise ValueError('Workers string is empty!')
            text_message = f'Сегодня работают:\n\nСменщики:\n{today_2_2_employers}'\
                        f'\nПятидневщики:\n{today_5_2_employers}'
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
        else:
            today_2_2_employers = get_today_workers(
                path=config.CSV_PATH, 
                current_day=current_day, 
                shift="2/2", 
                chat=False
            )
            if today_2_2_employers is None:
                raise ValueError('String is empty!')
            else:
                message = text_message = f'Сегодня работают:\n\nСменщики:\n{today_2_2_employers}'
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

def send_chatter_list(chat_id, current_day):
    try:
        today_chatters = get_today_workers(
            path=config.CSV_PATH,
            current_day=current_day,
            shift="2/2",
            chat=True
        )
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
                text = f"[{employer_name}](tg://user?id={employer_telegram_id}) ушел(-ла) на обед."\
                    f"\nКоллеги, подмените пожалуйста его в чатах."
            )
            return schedule.CancelJob
        else:
            return schedule.CancelJob
    except Exception as error:
        logger.error(error, exc_info = True)

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
            current_week_day = datetime.date.today().isoweekday()
            send_today_workers(message.chat.id, current_day, current_week_day)
        else:
            sign = ''
            numeric_value = ''
            print(message.text)
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

            send_today_workers(message.chat.id, past_day, past_week_day)
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
TODAY_CHATTERS_TIME = "09:10"
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
