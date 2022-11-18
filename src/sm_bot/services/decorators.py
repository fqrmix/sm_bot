from telebot import types, TeleBot

def on_private_chat_only(send_message):
    def __wrapper(message: types.Message, bot: TeleBot):
        if message.chat.type != 'private':
            bot.send_message(
                chat_id=message.chat.id, 
                text='Эта функция предназначена только для использания в личке у бота!',
                parse_mode='Markdown'
            )
        else:
            send_message(message, bot)
    return __wrapper