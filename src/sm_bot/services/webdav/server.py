from sm_bot.config import config
from sm_bot.services.logger import logger
from sm_bot.services.webdav import Client
import csv

class WebDAV:
    def __init__(self, path=None) -> None:
        if path is not None:
            self.employee_list = self.get_employee_list(path)
        else:
            self.employee_list = self.get_employee_list(config.Config.CSV_PATH)
        self.employeеs_info = config.Config.employers_info
    
    def get_webdav_info(self, telegram_id):
        try:
            webdav_info = {}
            for employee in self.employeеs_info:
                current_employee = self.employeеs_info[employee]
                if current_employee['telegram_id'] == telegram_id:
                    webdav_info['name'] = current_employee['webdav']['name']
                    webdav_info['url'] = current_employee['webdav']['url']
                    webdav_info['login'] = current_employee['telegram']
                    webdav_info['password'] = current_employee['webdav']['password']
            return webdav_info
        except Exception as error:
            logger.error(error, exc_info=True)

    def save_info(self):
        try:
            with open(config.Config.JSON_DIR_PATH + 'employers_info.json', 'w', encoding='utf-8') as info_json:    
                config.json.dump(self.employeеs_info, info_json, indent=4, ensure_ascii=False)
        except Exception as error:
            logger.error(error, exc_info=True)
    
    def generate_calendar(self, month):
        try:
            for c_w in self.employee_list:
                current_employee_name = c_w[config.Config.months[str(month)]]
                current_employee_info = self.employeеs_info[current_employee_name]
                actual_employee_login = current_employee_info['telegram']
                actual_employee_password = current_employee_info['webdav']['password']
                current_client = Client(actual_employee_login, actual_employee_password)
                vacation_flag = False
                vacation_day_start = 0
                vacation_day_end = 0
                for item in c_w:
                    if c_w[item] != '' and c_w[item] != 'ОТ' and c_w[item] != current_employee_name:
                        shift_start = config.Config.working_shift[c_w[item][0]]['start'].split(':')
                        shift_end = config.Config.working_shift[c_w[item][0]]['end'].split(':')
                        int_shift_start = int(shift_start[0])
                        int_shift_end = int(shift_end[0])
                        int_day_start = int(item)
                        int_day_end = int(item)
                        if int_shift_start == 12 and int_shift_end == 0:
                            int_day_end = int(item) + 1
                        current_client.create_event(
                            date_start=int_day_start,
                            date_end=int_day_end,
                            month=month,
                            time_start=int_shift_start,
                            time_end=int_shift_end,
                            summary='Смена'
                        )
                        logger.info(f'[WebDAV] [{current_employee_name}] Created event for {item} of {config.Config.months[str(month)]}')

                    if c_w[item] == 'ОТ' and c_w[item] != current_employee_name:
                        if not vacation_flag:
                            vacation_flag = True
                            vacation_day_start = int(item)
                            vacation_day_end = vacation_day_start
                        else:
                            vacation_day_end = int(item)
                    if c_w[item] != 'ОТ' and vacation_flag and c_w[item] != current_employee_name:
                        vacation_flag = False
                if vacation_day_start > 0 and vacation_day_end > 0:
                    current_client.create_event(
                                date_start=vacation_day_start,
                                date_end=vacation_day_end,
                                month=month,
                                time_start=0,
                                time_end=12,
                                summary='Отпуск'
                            )
                self.employeеs_info[current_employee_name]['webdav']['url'] = str(current_client.work_calendar_url)
                self.save_info()
        except Exception as error:
            logger.error(error, exc_info=True)
                        

    @staticmethod
    def get_employee_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employee_list = list(csv_reader)
        return employee_list