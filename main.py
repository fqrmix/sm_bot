from multiprocessing.context import Process
import csv
import time
import locale
import datetime
import logging
import schedule
import telebot
import config
import os

# RU locale
locale.setlocale(locale.LC_ALL, '')

# Logger
logger = telebot.logger
logger.setLevel(logging.INFO)
logging.basicConfig(filename='telegram-bot.log', level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

# Telegram Bot init
bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

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

def create_employer_str(employer_list, current_day, current_month):
    '''
        Function that create string which will be sent to Telegram API
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

                shift_start = config.working_shift[current_employer[current_day]]['start']
                shift_end = config.working_shift[current_employer[current_day]]['end']

                text_message += f"[{actual_employer_name}](tg://user?id={actual_employer_telegramid})"\
                f" | `{actual_employer_group}`" \
                f" | Cмена: `{shift_start}` - `{shift_end}`\n"

        logger.info(f"[today-employers] Employers string has been successfully generated!\n\n{text_message}")
        return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

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
            return key
    return None

# Get list of today employers
def get_today_employers(path, shift="2/2"):
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
                current_day = str(datetime.date.today().day)
                current_month = config.months[str(datetime.date.today().month)]
            text_message = create_employer_str(employer_list, current_day, current_month)
            return text_message
    except Exception as error:
        logger.error(error, exc_info = True)
        return None

# Send message of today employers
def send_today_employers(chat_id):
    '''
        Function that send strings from get_today_employers() to Telegram Chat.
        _______
        Arguments:
            *chat_id == Id of Telegram Chat
    '''
    try:
        current_week_day = datetime.date.today().isoweekday()
        if current_week_day in range(1,6):
            today_2_2_employers = get_today_employers(config.CSV_PATH, shift="2/2")
            today_5_2_employers = get_today_employers(config.CSV_PATH_5_2, shift="5/2")            
            if today_2_2_employers is None or today_5_2_employers is None:
                raise ValueError('String is empty!')
            text_message = f'Сегодня работают:\n\nСменщики:\n{today_2_2_employers}'\
                        f'\nПятидневщики:\n{today_5_2_employers}'
            bot.send_message(
                chat_id = chat_id,
                parse_mode = 'Markdown',
                text = text_message)
            logger.info(f'[today-employers] Message has been successfully sent! \n\n {text_message}')
        else:
            today_2_2_employers = get_today_employers(config.CSV_PATH, shift="2/2")
            if today_2_2_employers is None:
                raise ValueError('String is empty!')
            else:
                text_message = f'Сегодня работают:\n\nСменщики:\n{today_2_2_employers}'
                bot.send_message(
                    chat_id = chat_id,
                    parse_mode = 'Markdown',
                    text = text_message)
                logger.info(f'[today-employers] Message has been successfully sent! \n\n {text_message}')
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
            question = 'Доброе утро, Шопмастерская!\nВо сколько обед?',
            is_anonymous = False,
            options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'])
        logger.info(f'[lunch-poll] Lunch poll has been successfully sent in chatID: {chat_id}!')
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
        logger.info(f"[init] Initialization was completed in chatID - {message.chat.id}, chatName - {message.chat.title}, by user - @{message.from_user.username}")
    except Exception as error:
        logger.error(error, exc_info = True)

# Loading .csv file
@bot.message_handler(commands=['load'])
def load_message(message):
    '''
        Telegram handler of command /load, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    employer_name = get_employer_name(
        val = message.from_user.username,
        parameter = "telegram",
        my_dict = config.employers_info)
    if employer_name is None:
        bot.send_message(
            chat_id = message.chat.id,
            text = "Данная команда предназначена только для сотрудников тех. сопровождения/подключения!")
        error_msg = f"[load] User @{message.from_user.username} use command /load in chatID - {message.chat.id}, chatName - {message.chat.title}, but he doesn't exist in employers database!"
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
            bot.send_message(message.chat.id, f"I am waiting for CSV file!\nNot for {message.content_type}!\nUse /cancel command to quit")
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
@bot.message_handler(commands=['today'])
def today_employers(message):
    '''
        Telegram handler of command /today, which send list of today employers.
        _______
        Arguments:
            *message == Object of message
    '''
    send_today_employers(message.chat.id)

# Repeat lunch poll
@bot.message_handler(commands=['lunch'])
def reapeat_lunch(message):
    '''
        Telegram handler of command /lunch, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    send_lunch_query(message.chat.id)

# Out for lunch
@bot.message_handler(commands=['out'])
def get_out(message):
    '''
        Telegram handler of command /out, send notification about employers goes for lunch,
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        employer_telegram_id = message.from_user.id
        print(employer_telegram_id)
        employer_name = get_employer_name(
            val = str(employer_telegram_id),
            parameter = 'telegram_id',
            my_dict = config.employers_info)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для сотрудников тех. сопровождения/подключения!")
            error_msg = f"[out] User @{message.from_user.username} use command /out in chatID - {message.chat.id}, chatName - {message.chat.title}, but he doesn't exist in employers database!"
            raise ValueError(error_msg)
        bot.send_message(
            chat_id = message.chat.id,
            parse_mode = "Markdown",
            text = f"[{employer_name}](tg://user?id={employer_telegram_id}) ушел на обед.\nКоллеги, подмените пожалуйста его в чатах.")
        logger.info(f"[out] User @{message.from_user.username} successfully use command /out in chatID - {message.chat.id}, chatName - {message.chat.title}")
    except Exception as error:
        logger.error(error, exc_info = True)

# Get log into chat
@bot.message_handler(commands=['log'])
def get_log(message):
    try:
        readed_log = os.system("tail -n 30 telegram-bot.log")
        print(readed_log)
        bot.send_message(
            chat_id = message.chat.id,
            parse_mode = "Markdown",
            text = readed_log)
    except Exception as error:
        logger.error(error, exc_info = True)

########################
####### Shedule ########
########################

class ScheduleMessage():
    """Class for running shedules as isolated process"""

    @staticmethod
    def try_send_schedule():
        '''Trying to run_pending() method of shedule'''
        while True:
            schedule.run_pending()
            time.sleep(1)

    @staticmethod
    def start_process():
        '''Starting isolated process'''
        shedule_process = Process(target=ScheduleMessage.try_send_schedule, args=())
        shedule_process.start()


# Send today employers message to SM/POISK chat groups
schedule.every().day.at("08:00").do(send_today_employers, chat_id = config.GROUP_CHAT_ID_SM)
schedule.every().day.at("08:00").do(send_today_employers, chat_id = config.GROUP_CHAT_ID_POISK)

# Send today lunch-poll message to SM/POISK chat groups
schedule.every().day.at("10:00").do(send_lunch_query, chat_id = config.GROUP_CHAT_ID_SM)
schedule.every().day.at("10:00").do(send_lunch_query, chat_id = config.GROUP_CHAT_ID_POISK)


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
        ScheduleMessage.start_process()
        bot.infinity_polling()
    else:
        logger.info("[main] New CSV doesn't needed! Starting polling!")
        ScheduleMessage.start_process()
        bot.infinity_polling()
