from telebot import types, TeleBot
from sm_bot.services.logger import logger

# Send lunch poll
def send_lunch_query(chat_id, bot: TeleBot):
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

# Repeat lunch poll
def handle_lunch(message: types.Message, bot: TeleBot):
    '''
        Telegram handler of command /lunch, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        send_lunch_query(message.chat.id, bot)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

