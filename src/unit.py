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
from sm_bot.services.logger import logger
from sm_bot.services.subscription import Subscription
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


# Init
register_message_handlers(bot)
register_callback_handlers(bot)


class TestBotConnection(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = telebot.TeleBot(config.Config.TELEGRAM_TOKEN)

    def test_bot_send_message(self):
        current_date = datetime.date.today()
        self.assertIsNotNone(
            self.bot.send_message(
                chat_id=config.Config.GROUP_CHAT_ID_SM, 
                text=f'[{current_date}] Unit testing started successfully! [GROUP_CHAT_ID_SM message]'
            )
        )
        self.assertIsNotNone(
            self.bot.send_message(
                chat_id=config.Config.GROUP_CHAT_ID_POISK, 
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
        self.assertIsNotNone(self.dayworkers.send_message(chat_id=config.Config.GROUP_CHAT_ID_SM))
        self.assertIsNotNone(self.dayworkers.send_message(chat_id=config.Config.GROUP_CHAT_ID_POISK))

class TestChatters(unittest.TestCase):
    def setUp(self) -> None:
        self.chatters = Chatters()
    
    def test_chatters_init(self):
        self.assertIsNotNone(self.chatters.chatter_list)

    def test_chatter_list_send(self):
        self.assertIsNotNone(self.chatters.send_chatter_list(chat_id=config.Config.GROUP_CHAT_ID_SM))
        self.assertIsNotNone(self.chatters.send_chatter_list(chat_id=config.Config.GROUP_CHAT_ID_POISK))

    def test_chatter_list_job(self):
        self.assertIsNotNone(self.chatters.chatter_list_job('966243980'))

class TestSubscribtion(unittest.TestCase):
    def setUp(self) -> None:
        self.subscription = Subscription(test_run=True)
        self.dayworkers = DayWorkers()
        self.bot = telebot.TeleBot(config.Config.TELEGRAM_TOKEN)

    def test_sending_job(self):
        for employee in self.dayworkers.employees:
            actual_employee = self.dayworkers.create_actual_employee(
                    employee, 
                    self.dayworkers.current_day
                    )
            self.bot.send_message(
                chat_id=config.Config.GROUP_CHAT_ID_POISK, 
                text=f"{actual_employee['name']}"
            )
            self.assertIsNotNone(self.subscription.__sending_job__(actual_employee))

############################
## Start infinity polling ##
############################

if __name__ == '__main__':
    unittest.main()
