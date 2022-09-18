import datetime
from telebot import types, TeleBot
from sm_bot.handlers.workersmanager import *
from sm_bot.services.logger import logger

# Get list of today employers
def handle_workers(message: types.Message, bot: TeleBot):
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
                    # if int(past_day) > current_month_days:
                    #    past_day = str(int(past_day) - current_month_days
                    #    day_str = f"{past_day} числа следующего месяца будут работать:"
                    # else:
                    #    day_str = f"{past_day} числа текущего месяца будут работать:"
                elif sign == '-':
                    past_day = str(datetime.date.today().day - int(numeric_value))
                    day_str = f"{past_day} числа текущего месяца работали:"
            anyday_workers = DayWorkers(current_day=past_day)
            anyday_workers.send_message(
                chat_id = message.chat.id,
                current_day_text= day_str
                )
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)