import os
import json
from dotenv import load_dotenv
from sm_bot import ROOT_DIR, TEST_ROOT_DIR

load_dotenv()

config_type = os.environ.get('CONFIG_TYPE')
if config_type == 'Production':
    ROOT_DIR_PATH = ROOT_DIR
elif config_type == 'Test':
    ROOT_DIR_PATH = TEST_ROOT_DIR


class Config:
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    GROUP_CHAT_ID_SM = int(os.environ.get('GROUP_CHAT_ID_SM'))
    GROUP_CHAT_ID_POISK = int(os.environ.get('GROUP_CHAT_ID_POISK'))
    GROUP_CHAT_ID_MIDDLE_MNG = int(os.environ.get('GROUP_CHAT_ID_MIDDLE_MNG'))
    GROUP_CHAT_ID_MASS_MNG = int(os.environ.get('GROUP_CHAT_ID_MASS_MNG'))

    # Const
    ROOT_DIR = ROOT_DIR_PATH
    JSON_DIR_PATH = ROOT_DIR + '/data/json/'
    CSV_DIR_PATH = ROOT_DIR + '/data/csv/'
    print(ROOT_DIR)

    CSV_PATH = CSV_DIR_PATH + 'employers.csv'
    CSV_PATH_5_2 = CSV_DIR_PATH + 'employers_5_2.csv'
    NEXT_MONTH_CSV_PATH = CSV_DIR_PATH + 'employers-next.csv'

    # Import from json
    with open(JSON_DIR_PATH + 'employers_shift.json', 'r', encoding='utf-8') as shift_json:
        working_shift = json.load(shift_json)

    with open(JSON_DIR_PATH + 'employers_month.json', 'r', encoding='utf-8') as month_json:
        months = json.load(month_json)

    with open(JSON_DIR_PATH + 'employers_info.json', 'r', encoding='utf-8') as info_json:
        employers_info = json.load(info_json)

    with open(JSON_DIR_PATH + 'tech_data.json', 'r', encoding='utf-8') as tech_data_json:
        tech_data = json.load(tech_data_json)
