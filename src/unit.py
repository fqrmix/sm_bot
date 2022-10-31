import threading
import time
import locale
import datetime
import uuid
import schedule
import unittest
import telebot
from sm_bot.config import config
from sm_bot.handlers.chattersmanager.chatters import Chatters
from sm_bot.handlers.workersmanager.day_workers import DayWorkers
from sm_bot.services.bot import bot
from sm_bot.services.logger import logger, trace_logger
from sm_bot.services.subscription import Subscription
from sm_bot.handlers.workersmanager import today_workers
from sm_bot.handlers.chattersmanager import today_chatters
from sm_bot.handlers.bot.message.base import *
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


# Init
register_message_handlers(bot)
register_callback_handlers(bot)


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
    lunchquery.send_lunch_query,
    chat_id=config.GROUP_CHAT_ID_SM
)
schedule.every().day.at(TODAY_LUNCH_TIME).do(
    lunchquery.send_lunch_query, 
    chat_id=config.GROUP_CHAT_ID_POISK
)

class TestBotConnection(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

    def test_bot_send_message(self):
        current_date = datetime.date.today()
        self.assertIsNotNone(
            self.bot.send_message(
                chat_id=config.GROUP_CHAT_ID_SM, 
                text=f'[{current_date}] Unit testing started successfully! [GROUP_CHAT_ID_SM message]'
            )
        )
        self.assertIsNotNone(
            self.bot.send_message(
                chat_id=config.GROUP_CHAT_ID_POISK, 
                text=f'[{current_date}] Unit testing started successfully! [GROUP_CHAT_ID_POISK message]'
            )
        )

class TestDayWorkers(unittest.TestCase):
    def setUp(self) -> None:
        self.dayworkers = DayWorkers()

    def test_dayworkers_init(self):
        self.assertNotEqual(self.dayworkers.workers_list, [])

    def test_split_by_group(self):
        self.assertNotEqual(self.dayworkers.split_by_group(), None)

    def test_workers_send_message(self):
        self.assertEqual(self.dayworkers.send_message(chat_id=config.GROUP_CHAT_ID_SM), 200)
        self.assertIsNotNone(self.dayworkers.send_message(chat_id=config.GROUP_CHAT_ID_POISK), 200)

class TestChatters(unittest.TestCase):
    def setUp(self) -> None:
        self.chatters = Chatters()
    
    def test_chatters_init(self):
        self.assertNotEqual(self.chatters.chatter_list, [])

    def test_chatter_list_job(self):
        self.assertIsNotNone(self.chatters.chatter_list_job('966243980'))

class TestSubscribtion(unittest.TestCase):
    def setUp(self) -> None:
        self.subscription = Subscription(test_run=True)
        self.dayworkers = DayWorkers()

    def test_sending_job(self):
        for employee in self.dayworkers.employees:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' + self.dayworkers.current_day)
            print(employee['name'])
            actual_employee = self.dayworkers.create_actual_employee(
                    employee, 
                    self.dayworkers.current_day
                    )
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'  + actual_employee)
            self.assertIsNotNone(self.subscription.__sending_job__(
                actual_employee
            ))
    
    def test_create_schedule(self):
        ...

class TestSchedule(unittest.TestCase):
    def setUp(self) -> None:
        ...
        

############################
## Start infinity polling ##
############################

if __name__ == '__main__':
    unittest.main()
