from telebot import types, TeleBot
from sm_bot.services.logger import logger

def init_bot(message: types.Message, bot: TeleBot):
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


