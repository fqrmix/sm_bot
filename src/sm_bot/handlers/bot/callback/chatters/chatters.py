from telebot import types, TeleBot

from sm_bot.services.logger import logger
from sm_bot.handlers.chattersmanager import today_chatters

def handle_chatter_callback(call: types.CallbackQuery, bot: TeleBot):
    try:
        if call.data.startswith('chatter_'):
            telegram_id = call.data.replace('chatter_', '')
            today_chatters.add_chatter(telegram_id)
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = 'Готово, сообщение для сотрудника отправлено в соответствующий чат!', 
                reply_markup = '')
            
        elif call.data.startswith('removechatter_'):
            telegram_id = call.data.replace('removechatter_', '')
            today_chatters.remove_chatter(telegram_id)
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = 'Готово, сообщение для сотрудника отправлено в соответствующий чат!', 
                reply_markup = '')
        
        elif call.data == 'chatter_cancel':
            bot.delete_message(call.message.chat.id, call.message.message_id)
        
    except Exception as error:
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)