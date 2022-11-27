import threading
import time
import locale
import datetime
import schedule
import cherrypy
from isdayoff import DateType
from webhook import server
from sm_bot.config import config
from sm_bot.handlers.workersmanager.day_workers import DayWorkers
from sm_bot.services.bot import bot
from sm_bot.services.subscription import Subscription
from sm_bot.handlers.workersmanager import today_workers
from sm_bot.handlers.chattersmanager import today_chatters
from sm_bot.handlers.bot.message.base import *
from sm_bot.handlers.bot.message import register_message_handlers
from sm_bot.handlers.bot.callback import register_callback_handlers

# RU locale
locale.setlocale(locale.LC_ALL, '')

# Init
Subscription().create_schedule()
register_message_handlers(bot)
register_callback_handlers(bot)


########################
####### Sсhedule #######
########################

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

current_date = datetime.date.today()

# Send today employers message to SM/POISK chat groups
TODAY_EMPOYERS_TIME = "08:00"
schedule.every().day.at(TODAY_EMPOYERS_TIME).do(
    today_workers.send_message, 
    chat_id=config.Config.GROUP_CHAT_ID_SM
)
schedule.every().day.at(TODAY_EMPOYERS_TIME).do(
    today_workers.send_message, 
    chat_id=config.Config.GROUP_CHAT_ID_POISK,
)

# Send chatters list message to SM/POISK chat groups
TODAY_CHATTERS_TIME = "08:30"
if DayWorkers.get_dayoff_info(current_date) is DateType.WORKING:
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        today_chatters.send_chatter_list,
        chat_id=config.Config.GROUP_CHAT_ID_SM,
    )
    schedule.every().day.at(TODAY_CHATTERS_TIME).do(
        today_chatters.send_chatter_list, 
        chat_id=config.Config.GROUP_CHAT_ID_POISK,
    )

# Send today lunch-poll message to SM/POISK chat groups
TODAY_LUNCH_TIME = "10:00"
schedule.every().day.at(TODAY_LUNCH_TIME).do(
    lunchquery.send_lunch_query,
    chat_id=config.Config.GROUP_CHAT_ID_SM
)
schedule.every().day.at(TODAY_LUNCH_TIME).do(
    lunchquery.send_lunch_query, 
    chat_id=config.Config.GROUP_CHAT_ID_POISK
)

if __name__ == '__main__':
    bot.delete_webhook()
    bot.set_webhook(url="https://webhook.fqrmix.ru/sm_bot/")
    stop_run_continuously = run_continuously()
    cherrypy.quickstart(server.WebhookServer(bot), '/', {'/': {}})
    stop_run_continuously.set()
