import csv
import sm_bot.config.config as config
from sm_bot.services.logger import logger

class Employees:
    def __init__(self, next_month=False) -> None:
        try:
            if not next_month:
                employees_list = self.get_employer_list(config.CSV_PATH)
            else:
                employees_list = self.get_employer_list(config.NEXT_MONTH_CSV_PATH)
            logger.info(msg="[employees] Shift employees list was dumped from CSV")
            fulltime_employees_list = self.get_employer_list(config.CSV_PATH_5_2)
            logger.info(msg="[employees] Fulltime employees list was dumped from CSV")
            self.employees = []
            self.fulltime_employees = []
            actual_employee = {
                'name': '',
                'shifts': {}
            }

            logger.info(msg="[employees] Creating in-self class lists")
            # Creating 2/2 employees list
            for employee in employees_list:
                for current_employee in employee:
                    if len(employee[current_employee]) > 2:
                        actual_employee['name'] = employee[current_employee]
                    else:
                        actual_employee['shifts'][current_employee] = employee[current_employee]
                self.employees.append(actual_employee)
                actual_employee = {
                    'name': '',
                    'shifts': {}
                }
            
            # Creating 5/2 employess list
            for employee in fulltime_employees_list:
                actual_employee['name'] = employee['5/2']
                actual_employee['shifts']['Any'] = employee['Any']
                self.fulltime_employees.append(actual_employee)
                actual_employee = {
                    'name': '',
                    'shifts': {}
                }
            logger.info(msg=f"[employees] In-self class lists was created.")
        except Exception as error:
            logger.error(error, exc_info=True)

    @staticmethod
    def get_employer_list(path):
        with open(path, encoding = 'utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            employer_list = list(csv_reader)
        return employer_list

    @staticmethod
    def get_employer_name(val: str, parameter: str, my_dict: dict):
        '''
            Function that return employer name by paramater.
            If paramater doesn't exists in my_dict - return None instead.
            _______
            Arguments:
                *val == Parameter which searched
                *parametr == Search parameter
                *my_dict == Dict
        '''
        for key, value in my_dict.items():
            if val == value[parameter]:
                return key, value
        return None, None

    @staticmethod
    def save_employees_list(path: str, employees: list, workers_fieldnames: list):
        with open(path, 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=workers_fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(employees)

