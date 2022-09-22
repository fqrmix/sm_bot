import csv
import datetime
import sm_bot.config.config as config
from sm_bot.services.logger import logger
from sm_bot.services.bot import bot
from sm_bot.handlers.workersmanager.employees import Employees



###################
## Workers block ##
###################


class DayWorkers(Employees):
    def __init__(self, current_day=None) -> None:
        super().__init__()
        if current_day is None:
            self.current_day = str(datetime.date.today().day)
            self.week_day = datetime.date.today().isoweekday()
        else:
            self.current_day = current_day
            now = datetime.datetime.now()

            past_week_day = datetime.date(
                year=now.year,
                month=now.month,
                day=int(current_day)).isoweekday()
            self.week_day = past_week_day
    
        self.workers_list = []

        for current_employer in self.employees:
            if current_employer['shifts'][self.current_day] != '' \
            and current_employer['shifts'][self.current_day] != 'ОТ'\
            and current_employer['shifts'][self.current_day] != 'DO':
                actual_employee = self.create_actual_employee(
                    current_employer, 
                    self.current_day
                    )
                if len(current_employer['shifts'][self.current_day]) > 1 \
                and current_employer['shifts'][self.current_day][1] == "ч":
                    actual_employee['chat']['state'] = True
                self.workers_list.append(actual_employee)

        if self.week_day in range(1,6):
            for current_employer in self.fulltime_employees:
                if current_employer['shifts']['Any'] != '' \
                and current_employer['shifts']['Any'] != 'ОТ':
                    actual_employee = self.create_actual_employee(
                        current_employer, 
                        'Any'
                        )
                    self.workers_list.append(actual_employee)
        logger.info(msg=f"[day-workers] DayWorkers class was initilated. Scope: {self.workers_list}")

    def split_by_group(self) -> list:
        try:
            shopmasters_list = []
            poisk_list = []
            others_list = []
            for current_employer in self.workers_list:
                if current_employer['group'] == 'ShopMaster':
                    shopmasters_list.append(current_employer)
                elif current_employer['group'] == 'Poisk':
                    poisk_list.append(current_employer)
                else:
                    others_list.append(current_employer)
            shopmasters_list.sort(key=self.sort_by_shift)
            poisk_list.sort(key=self.sort_by_shift)
            others_list.sort(key=self.sort_by_shift)
            logger.info(msg=f"[day-workers] Workers list was successfully splited by group")
            return shopmasters_list, poisk_list, others_list
        except Exception as error:
            logger.error(error, exc_info = True)

    def send_message(self, chat_id, current_day_text='Сегодня работают:') -> str:
        try:
            shopmasters_list, poisk_list, others_list = self.split_by_group()

            current_day_sm = self.create_str(shopmasters_list) 
            current_day_sm_text = f'*Шопмастера:*\n{current_day_sm}'\
                if shopmasters_list != [] else ''

            current_day_poisk = self.create_str(poisk_list)
            current_day_poisk_text = f'*Поиск:*\n{current_day_poisk}'\
                if poisk_list != [] else ''

            current_day_others = self.create_str(others_list)
            current_day_others_text = f'*CMS/LK:*\n{current_day_others}'\
                if others_list != [] else ''

            text_message = f'*{current_day_text}*\n\n{current_day_sm_text}\n'\
                            f'{current_day_poisk_text}\n'\
                            f'{current_day_others_text}'
            
            bot_message = bot.send_message(
                chat_id = chat_id,
                parse_mode = 'Markdown',
                text = text_message
            )

            logger.info(msg=f"[day-workers] Workers message was successfully send to chatID: {chat_id}")
            if current_day_text == 'Сегодня работают:':
                bot.pin_chat_message(
                        chat_id=chat_id,
                        message_id=bot_message.id
                )
                logger.info(msg=f"[day-workers] Workers message was successfully pinned to chatID: {chat_id}")
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def _update(self) -> None:
        self.__init__()

    """
    Workers class static methods
    """

    @staticmethod
    def get_employer_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        return employer_list

    @staticmethod
    def sort_by_shift(employee): 
        return employee['shift_start']

    @staticmethod
    def create_actual_employee(current_employer, current_day):
        try:
            actual_employee_name = current_employer['name']
            actual_employee_info = config.employers_info[actual_employee_name]
            actual_employee_group = actual_employee_info['group']
            actual_employee_telegramid = actual_employee_info['telegram_id']

            shift_start = config.working_shift[current_employer['shifts'][current_day][0]]['start']
            shift_end = config.working_shift[current_employer['shifts'][current_day][0]]['end']

            actual_employee = {
                'name': actual_employee_name,
                'group': actual_employee_group,
                'telegram_id': actual_employee_telegramid,
                'shift_start': shift_start,
                'shift_end': shift_end,
                'chat': {
                    'state': False,
                    'lunch_time': None,
                    'scheduled': False
                }
            }
            logger.info(msg=f"[day-workers] Actual employee dict was generated. Subject: {actual_employee}")
            return actual_employee
        except Exception as error:
            logger.error(error, exc_info = True)
    
    @staticmethod
    def create_str(group_list):
        text_message = ''
        for employee in group_list:
            if employee['group'] == 'CMS' or employee['group'] == 'LK':
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | `{employee['group']}`" \
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
            else:
                text_message += f"[{employee['name']}](tg://user?id={employee['telegram_id']})"\
                f" | Cмена: `{employee['shift_start']}` - `{employee['shift_end']}`\n"
        return text_message