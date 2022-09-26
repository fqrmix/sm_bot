from telebot import types, TeleBot
from sm_bot.services.subscription import Subscription
from sm_bot.services.logger import logger

# Subscription menu callback handler
def handle_sub_callback(call: types.CallbackQuery, bot: TeleBot):
    try:
        if call.data == 'sub_change_status':
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = 'Выбери действие [Включить/Отключить]', 
                reply_markup = Subscription.build_keyboard('change_sub_actions'))
        
        elif call.data == 'sub_enable':
            telegram_id = call.from_user.id
            sub_info = Subscription.get_sub_info(telegram_id)
            if sub_info['enabled']:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Подписка уже активна!'
                )
            else:
                Subscription.enable(telegram_id)
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Подписка была успешно включена!'
                )

        elif call.data == 'sub_disable':
            telegram_id = call.from_user.id
            sub_info = Subscription.get_sub_info(telegram_id)
            if not sub_info['enabled']:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Подписка уже отключена!'
                )
            else:
                Subscription.disable(telegram_id)
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Подписка была успешно отключена!'
                )
        
        elif call.data == 'sub_change_time':
            telegram_id = call.from_user.id
            sub_info = Subscription.get_sub_info(telegram_id)
            if not sub_info['enabled']:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text='Подписка отключена!'\
                        'Необходимо ее включить для редактирования времени уведомления!'
                )
            else:
                inner_message = bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='Пришли мне время в формате XX:YY',
                    reply_markup=Subscription.build_keyboard('back_to_main_keyboard')
                )
                bot.register_next_step_handler(inner_message, Subscription.handle_change_subtime, telegram_id=telegram_id)

        elif call.data == 'sub_back_to_main':
            bot.clear_step_handler(call.message)
            telegram_id = call.from_user.id
            sub_info = Subscription.get_sub_info(telegram_id)
            sub_status = 'Включена' if sub_info['enabled'] else 'Отключена'
            sub_notify_time = sub_info['time_to_notify']
            text_message = f"Статус подписки: {sub_status}\n"\
                        f"Время для уведомлений: {sub_notify_time}" if sub_info['enabled'] else \
                        f"Статус подписки: {sub_status}"
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id = call.message.message_id,
                text = text_message, 
                reply_markup = Subscription.build_keyboard('main_sub')
            )
    except Exception as error:
        logger.error(error, exc_info = True)