import telebot
import sm_bot.config.config as config

bot = telebot.TeleBot(config.Config.TELEGRAM_TOKEN)