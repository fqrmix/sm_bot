import logging
import telebot

# Logger
logger = telebot.logger
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
file_handler = logging.FileHandler('./logs/telegram-bot.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

trace_logger = logging.getLogger('logger')
trace_logger .setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - [%(trace_id)s] - %(message)s')
file_handler = logging.FileHandler('./logs/telegram-bot.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
trace_logger.addHandler(file_handler)
