from telebot import types, TeleBot
from sm_bot.services.webdav import WebDAV
from sm_bot.services.logger import logger
from sm_bot.services.decorators import on_private_chat_only, b2btech_only

@b2btech_only
@on_private_chat_only
def web_dav_menu(message: types.Message, bot: TeleBot):
    try:
        telegram_id = message.from_user.id
        webdav_info = WebDAV().get_webdav_info(str(telegram_id))
        text_message = f"*Название календаря:* `{webdav_info['name']}`\n"\
                        f"*URL календаря:* {webdav_info['url']}\n\n"\
                        f"*Информация для подключения к серверу:*\n\n"\
                        f"*Адрес:* https://webdav.fqrmix.ru\n"\
                        f"*Логин:* `{webdav_info['login']}`\n"\
                        f"*Пароль:* `{webdav_info['password']}`"
        bot.send_message(
            chat_id=message.chat.id,
            text=text_message,
            parse_mode='markdown'
        )
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)
