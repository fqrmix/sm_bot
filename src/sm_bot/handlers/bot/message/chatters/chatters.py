from sm_bot.handlers.chattersmanager import *
from sm_bot.handlers.workersmanager.employees import Employees
from sm_bot.services.logger import logger
from sm_bot.config import config
from telebot import types, TeleBot
import schedule

# Send chatters list
def handle_chatters(message: types.Message, bot: TeleBot):
    try:
        today_chatters.send_chatter_list(message.chat.id)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

# Add chatter to list
def handle_add_chatters(message: types.Message, bot: TeleBot):
    try:
        today_chatters.add_chatter_message(message)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

# Remove chatter from list
def handle_remove_chatters(message: types.Message, bot: TeleBot):
    try:
        today_chatters.remove_chatter_message(message)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

# Chatter list job
def chatter_list_job(employer_telegram_id, bot: TeleBot):
    try:
        chat_id = None
        employer_name, employer_info = Employees.get_employer_name(
            val=str(employer_telegram_id),
            parameter='telegram_id', 
            my_dict=config.employers_info
        )
        if employer_info['group'] == 'ShopMaster':
            chat_id = config.GROUP_CHAT_ID_SM
        elif employer_info['group'] == 'Poisk':
            chat_id = config.GROUP_CHAT_ID_POISK
        if chat_id is not None:
            bot.send_message(
                chat_id = chat_id,
                parse_mode = "Markdown",
                text = f"[{employer_name}](tg://user?id={employer_telegram_id}) скоро уйдет на обед."\
                    f"\nКоллеги, подмените пожалуйста его в чатах."
            )
            logger.info(msg=f"[chatter-job] Chatter job was completed for {employer_name}")
            return schedule.CancelJob
        else:
            return schedule.CancelJob
    except Exception as error:
        logger.error(error, exc_info = True)

# Auto-out for lunch
def handle_poll_answer(pollAnswer: types.PollAnswer, bot: TeleBot):
    if len(pollAnswer.option_ids) > 0:
        lunch_time = get_lunch_time(pollAnswer.option_ids[0])
        logger.info(f'[poll-answer-handler] User {pollAnswer.user.id} has choosen {lunch_time} time for lunch')
        try:
            for current_chatter in today_chatters.chatter_list:
                if current_chatter['telegram_id'] == str(pollAnswer.user.id):
                    logger.info(f"[poll-answer-handler] User {pollAnswer.user.id} was found in chatter list\n"\
                        f"Subject: {today_chatters.chatter_list}")
                    if current_chatter['chat']['scheduled']:
                        logger.info(f'[poll-answer-handler] Schedule for user {pollAnswer.user.id} was already created')
                        schedule.clear(str(pollAnswer.user.id))
                        logger.info(f'[poll-answer-handler] Previous schedule for user {pollAnswer.user.id} was removed')
                    schedule.every().day.at(lunch_time).do(
                        chatter_list_job,
                        bot = bot,
                        employer_telegram_id = pollAnswer.user.id
                    ).tag(str(pollAnswer.user.id))
                    logger.info(f'[poll-answer-handler] Schedule for lunch-out was created for user {pollAnswer.user.id}')
                    current_chatter['chat']['lunch_time'] = lunch_time
                    current_chatter['chat']['scheduled'] = True
                    logger.info(f"[poll-answer-handler] User {pollAnswer.user.id} "\
                        f"lunch time: {current_chatter['chat']['lunch_time']}, "\
                        f"schedule status: {current_chatter['chat']['scheduled']}")
        except Exception as error:
            logger.error(error, exc_info = True)