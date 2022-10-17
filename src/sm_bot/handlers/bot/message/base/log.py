from telebot import types, TeleBot
from sm_bot.services.logger import logger


# Get log n str
def get_log_str(log_name, lines):
    with open(log_name, encoding='utf-8') as file:
        result = ''
        for line in (file.readlines()[-lines:]):
            result += line
    return result

# Get log into chat
def handle_log(message: types.Message, bot: TeleBot):
    '''
        Telegram handler of command /log, which send log file into chat.
        _______
        Arguments:
            *message == Object of message
    '''
    value = (message.text).replace('/log ', '') # Number after /log message
    lines = 5 if value == '/log' else int(value) # 5 - default value, if value in message is empty
    log_to_bot = get_log_str(log_name='./logs/telegram-bot.log', lines=lines)
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
