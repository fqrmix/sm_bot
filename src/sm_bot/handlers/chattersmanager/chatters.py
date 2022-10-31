from sm_bot.handlers.workersmanager.day_workers import DayWorkers
from sm_bot.handlers.workersmanager.employees import Employees
import sm_bot.config.config as config
from sm_bot.services.bot import bot
from sm_bot.services.logger import logger
from telebot import types
import schedule

def get_lunch_time(option_id: int) -> str:
    options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00']
    return options[option_id]

def get_notification_time(str: str) -> str:
    new_str = str.split(':')
    time_hour = int(new_str[0]) - 1
    time_minutes = int(new_str[1]) + 55
    return f'{time_hour}:{time_minutes}'

def get_schedule_time(option_id: int) -> str:
    options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00']
    lunch_time = options[option_id]
    return get_notification_time(lunch_time)


########################
## Chatter list block ##
########################

class Chatters(DayWorkers):
    def __init__(self) -> None:
        super().__init__()
        self.chatter_list = []
        for current_emoloyer in self.workers_list:
            if current_emoloyer['chat']['state']:
                self.chatter_list.append(current_emoloyer)
        if self.chatter_list == []:
            logger.info(f"[chatters] Not found chatters for today")
        else:
            logger.info(f"[chatters] Found chatters for today. Scope: {self.chatter_list}")

    def print_list(self):
        for chatter in self.chatter_list:
            print(chatter)
    
    def create_chatters_str(self) -> str:
        try:
            text_message = ''
            for current_chatter in self.chatter_list:
                actual_employer_name = current_chatter['name']
                actual_employer_group = current_chatter['group']
                actual_employer_telegramid = current_chatter['telegram_id']
                text_message += f"[{actual_employer_name}](tg://user?id={actual_employer_telegramid})"\
                                f" | `{actual_employer_group}`\n"
            logger.info(msg=f"[chatters] Chatters string was created. Subject: {text_message}")
            return text_message
        except Exception as error:
            logger.error(error, exc_info = True)

    def send_chatter_list(self, chat_id) -> None:
        try:
            today_chatters = self.create_chatters_str()
            text_message = f"Сегодня в чатах:\n{today_chatters}"
            bot.send_message(
                chat_id=chat_id,
                parse_mode='Markdown',
                text=text_message
            )
            logger.info(f"[chatters] Chatter string was successfully sent into chatID: {chat_id}")
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def build_chatter_keyboard(self, direction: str) -> types.InlineKeyboardMarkup:
        try:
            chattter_menu_button_list = []
            if direction == 'in':
                keyboard = types.InlineKeyboardMarkup(row_width = 1)
                for current_employee in self.workers_list:
                    if current_employee not in self.chatter_list:
                        button = types.InlineKeyboardButton(
                            text = current_employee['name'], 
                            callback_data = 'chatter_' + current_employee['telegram_id'])
                        chattter_menu_button_list.append(button)
                back_button = types.InlineKeyboardButton(
                            text = '<< Отмена', 
                            callback_data = 'cancel')
                chattter_menu_button_list.append(back_button)
                keyboard.add(*chattter_menu_button_list)
                return keyboard
            elif direction == 'out':
                keyboard = types.InlineKeyboardMarkup(row_width = 2)
                for current_employee in self.chatter_list:
                    if current_employee in self.chatter_list:
                        button = types.InlineKeyboardButton(
                            text = current_employee['name'], 
                            callback_data = 'removechatter_' + current_employee['telegram_id'])
                        chattter_menu_button_list.append(button)
                back_button = types.InlineKeyboardButton(
                            text = '<< Отмена', 
                            callback_data = 'cancel')
                chattter_menu_button_list.append(back_button)
                keyboard.add(*chattter_menu_button_list)
                return keyboard
            else:
                raise ValueError('Wrong direction value in build_chatter_keyboard')
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def add_chatter_message(self, message):
        try:
            logger.info(msg=f"[chatters] User {message.from_user.username} trying to add chatter")
            today_chatters = self.create_chatters_str()
            text_message = f"Сейчас в чатах:\n{today_chatters}\n"\
                f"Выбери сотрудника для добавления:\n"
            markup_keyboard = self.build_chatter_keyboard(direction='in')
            bot.send_message(
                chat_id=message.chat.id,
                text=text_message,
                parse_mode='Markdown',
                reply_markup=markup_keyboard
            )
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def add_chatter(self, telegram_id: str) -> types.Message:
        try:
            chat_id = ''
            text_message = ''
            for current_emoloyer in self.workers_list:
                if current_emoloyer['telegram_id'] == telegram_id:
                    self.chatter_list.append(current_emoloyer)
                    current_emoloyer['chat']['state'] = True
                    if current_emoloyer['group'] == 'Poisk':
                        chat_id = config.GROUP_CHAT_ID_POISK
                    else:
                        chat_id = config.GROUP_CHAT_ID_SM
                    text_message = f"[{current_emoloyer['name']}](tg://user?id={current_emoloyer['telegram_id']}), "\
                        f"привет! Заходи, пожалуйста, в чаты."
                    message = bot.send_message(
                        chat_id=chat_id,
                        text=text_message,
                        parse_mode='Markdown'
                    )
                    logger.info(msg=f"[chatters] Chatter {current_emoloyer['name']} was successfully appended, "\
                        f"message was sent to chatID: {chat_id}")
                    return message
        except Exception as error:
            logger.error(error, exc_info = True)

    def remove_chatter_message(self, message: types.Message) -> None:
        try:
            logger.info(msg=f"[chatters] User {message.from_user.username} trying to remove chatter")
            today_chatters = self.create_chatters_str()
            text_message = f"Сейчас в чатах:\n{today_chatters}\n"\
                f"Выбери сотрудника для удаления:\n"
            markup_keyboard = self.build_chatter_keyboard(direction='out')
            bot.send_message(
                chat_id=message.chat.id,
                text=text_message,
                parse_mode='Markdown',
                reply_markup=markup_keyboard
            )
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def remove_chatter(self, telegram_id: str) -> types.Message:
        try:
            chat_id = ''
            text_message = ''
            for current_emoloyer in self.workers_list:
                if current_emoloyer['telegram_id'] == telegram_id:
                    self.chatter_list.remove(current_emoloyer)
                    current_emoloyer['chat']['state'] = False
                    if current_emoloyer['group'] == 'Poisk':
                        chat_id = config.GROUP_CHAT_ID_POISK
                    else:
                        chat_id = config.GROUP_CHAT_ID_SM
                    text_message = f"[{current_emoloyer['name']}](tg://user?id={current_emoloyer['telegram_id']}), "\
                        f"привет! Выходи, пожалуйста, из чатов и заходи в линию."
                    message = bot.send_message(
                        chat_id=chat_id,
                        text=text_message,
                        parse_mode='Markdown'
                    )
                    logger.info(msg=f"[chatters] Chatter {current_emoloyer['name']} was successfully removed, "\
                        f"\nmessage was sent to chatID: {chat_id}")
                    shedule_clear = schedule.clear(telegram_id)
                    return message
        except Exception as error:
            logger.error(error, exc_info = True)

    @staticmethod
    # Chatter list job
    def chatter_list_job(employer_telegram_id) -> schedule.CancelJob:
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
