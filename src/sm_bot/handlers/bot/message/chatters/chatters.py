from sm_bot.handlers.chattersmanager import *
from sm_bot.handlers.workersmanager.employees import Employees
from sm_bot.services.decorators import on_private_chat_only, exception_handler, b2btech_only
from sm_bot.handlers.bot.message.base import *
from sm_bot.services.logger import logger
from sm_bot.config import config
from telebot import types, TeleBot
import schedule
import operator

# Send chatters list
@exception_handler
def handle_chatters(message: types.Message, bot: TeleBot):
    today_chatters.send_chatter_list(message.chat.id)

# Add chatter to list
@b2btech_only
@on_private_chat_only
@exception_handler
def handle_add_chatters(message: types.Message, bot: TeleBot):
    today_chatters.add_chatter_message(message)

# Remove chatter from list
@b2btech_only
@on_private_chat_only
@exception_handler
def handle_remove_chatters(message: types.Message, bot: TeleBot):
    today_chatters.remove_chatter_message(message)

def _get_chatters_group_count(chatter_list: list):
    result = {
        "ShopMaster": 0,
        "Poisk": 0
    }

    for chatter in chatter_list:
        result[chatter['group']] += 1

    return result

def _filter_chatters_list(chatter_list: list):
    group_count = _get_chatters_group_count(chatter_list)
    result = list()
    for chatter in chatter_list:
        if(group_count[chatter['group']] == 1):
            result.append(chatter)
    
    return result

# Auto-out for lunch
def handle_poll_answer(pollAnswer: types.PollAnswer, bot: TeleBot) -> None:
    if len(pollAnswer.option_ids) == 0:
        for employee in lunchquery.lunch_list:
            if employee['id'] == pollAnswer.user.id:
                lunchquery.lunch_list.pop(lunchquery.lunch_list.index(employee))
                lunchquery.update_markup(bot)
    else:
        lunch_time = get_lunch_time(pollAnswer.option_ids[0])
        logger.info(f'[poll-answer-handler] User {pollAnswer.user.id} has choosen {lunch_time} time for lunch')
        employer_name, employer_info = Employees.get_employer_name(
            val=str(pollAnswer.user.id),
            parameter='telegram_id', 
            my_dict=config.Config.employers_info
        )
        in_lunch_list = False
        for single_employee in lunchquery.lunch_list:
            if single_employee['id'] == pollAnswer.user.id:
                if lunch_time != single_employee['lunch_time']:
                    single_employee['lunch_time'] = lunch_time
                    lunchquery.lunch_list.sort(key=operator.itemgetter('lunch_time'))
                    lunchquery.update_markup(bot)
                in_lunch_list = True

        if not in_lunch_list:
            lunch_employee = {
                'id': str,
                'name': str,
                'lunch_time': str
            }
            
            lunch_employee['id'] = pollAnswer.user.id
            lunch_employee['name'] = employer_name
            lunch_employee['lunch_time'] = lunch_time
            lunchquery.lunch_list.append(lunch_employee)
            lunchquery.lunch_list.sort(key=operator.itemgetter('lunch_time'))
            lunchquery.update_markup(bot)

        if (pollAnswer.option_ids[0] != 7):
            try:
                schedule_time = get_schedule_time(pollAnswer.option_ids[0])
                for current_chatter in _filter_chatters_list(today_chatters.chatter_list):
                    if current_chatter['telegram_id'] == str(pollAnswer.user.id):
                        logger.info(f"[poll-answer-handler] User [{employer_name} | ID: {pollAnswer.user.id}] was found in chatter list\n"\
                            f"Subject: {today_chatters.chatter_list}")
                        if current_chatter['chat']['scheduled']:
                            logger.info(f'[poll-answer-handler] Schedule for user [{employer_name} | ID: {pollAnswer.user.id}] was already created')
                            schedule.clear(str(pollAnswer.user.id))
                            logger.info(f'[poll-answer-handler] Previous schedule for user [{employer_name} | ID: {pollAnswer.user.id}] was removed')
                        try:
                            schedule.every().day.at(schedule_time).do(
                                today_chatters.chatter_list_job,
                                employer_telegram_id = pollAnswer.user.id
                            ).tag(str(pollAnswer.user.id))
                        except Exception as error:
                            logger.error(error, exc_info=True)
                        logger.info(f'[poll-answer-handler] Schedule for lunch-out was created for user [{employer_name} | ID: {pollAnswer.user.id}] | Time: {schedule_time}')
                        current_chatter['chat']['lunch_time'] = lunch_time
                        current_chatter['chat']['scheduled'] = True
                        logger.info(f"[poll-answer-handler] User [{employer_name} | ID: {pollAnswer.user.id}] "\
                            f"lunch time: {current_chatter['chat']['lunch_time']}, "\
                            f"schedule status: {current_chatter['chat']['scheduled']}")
            except Exception as error:
                logger.error(error, exc_info = True)
