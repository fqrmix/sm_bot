import threading
import time
import locale
import datetime
import uuid
import schedule
from sm_bot.config import config
from sm_bot.services.bot import bot
from sm_bot.services.logger import logger, trace_logger
from sm_bot.services.subscription import Subscription
from sm_bot.handlers.workersmanager.employees import Employees

from sm_bot.handlers.bot.message import register_message_handlers
from sm_bot.handlers.bot.callback import register_callback_handlers

# RU locale
locale.setlocale(locale.LC_ALL, '')

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

###########################
## Initialization block ###
###########################

logger_data = {
            'trace_id': uuid.uuid4()
        }

current_date = datetime.date.today()
if current_date.day == 1:
    trace_logger.info('[main] Time to new CSV...\nUpdating', extra=logger_data)
    update_actual_csv(config.NEXT_MONTH_CSV_PATH, config.CSV_PATH) # Update actual CSV file
    trace_logger.info('[main] CSV file was successfully loaded! Strarting polling!', extra=logger_data)
else:
    trace_logger.info("[main] New CSV doesn't needed! Starting polling!", extra=logger_data)

Subscription().create_schedule()

# Init
register_message_handlers(bot)
register_callback_handlers(bot)

# Loading .csv file
@bot.message_handler(commands=['load'])
def handle_loader(message):
    '''
        Telegram handler of command /load, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        employer_name, value = Employees.get_employer_name(
            val = message.from_user.username,
            parameter = "telegram",
            my_dict = config.employers_info)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для"\
                    "сотрудников тех. сопровождения/подключения!"
            )
            error_msg = f"[load] User @{message.from_user.username} use command /load in chatID "\
                f"- {message.chat.id}, chatName - {message.chat.title}, but he doesn't exist in employers database!"
            raise ValueError(error_msg)
        else:
            logger.info(f'[load] User "{message.from_user.username}" trying to load a new CSV file')
            link_message = bot.send_message(
                        chat_id = message.chat.id,
                        text = 'Пришли мне файл с графиком в формате .CSV на следующий месяц')
            bot.register_next_step_handler(link_message, load_employers_csv)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

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
            bot.send_message(
                chat_id=message.chat.id,
                text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
                parse_mode='markdown'
            )
            logger.error(error, exc_info = True)


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
        employer_name, value = Employees.get_employer_name(
            val = str(employer_telegram_id),
            parameter = 'telegram_id',
            my_dict = config.employers_info)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для"\
                    "сотрудников тех. сопровождения/подключения!"
            )
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


############################
## Start infinity polling ##
############################

if __name__ == '__main__':
    stop_run_continuously = run_continuously()
    bot.infinity_polling()
    stop_run_continuously.set()
