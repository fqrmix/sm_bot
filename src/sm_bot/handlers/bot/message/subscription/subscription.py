from telebot import types, TeleBot
from sm_bot.services.subscription import Subscription
from sm_bot.services.logger import logger
from sm_bot.services.decorators import on_private_chat_only

# Subscription menu
@on_private_chat_only
def handle_sub_menu(message: types.Message, bot: TeleBot):
    try:
        telegram_id = message.from_user.id
        sub_info = Subscription.get_sub_info(telegram_id)
        sub_status = 'Включена' if sub_info['enabled'] else 'Отключена'
        sub_notify_time = sub_info['time_to_notify']
        text_message = f"Статус подписки: {sub_status}\nВремя для уведомлений: {sub_notify_time}" if sub_info['enabled'] else \
                        f"Статус подписки: {sub_status}"
        bot.send_message(
            chat_id=message.chat.id, 
            text=text_message, 
            reply_markup=Subscription.build_keyboard('main_sub')
        )
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)