import os
import json
from dotenv import load_dotenv
from sm_bot import ROOT_DIR

# Get env variables
load_dotenv()
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROUP_CHAT_ID_SM = int(os.environ.get('GROUP_CHAT_ID_SM'))
GROUP_CHAT_ID_POISK = int(os.environ.get('GROUP_CHAT_ID_POISK'))

# Const
JSON_DIR_PATH = ROOT_DIR + '/data/json/'
CSV_DIR_PATH = ROOT_DIR + '/data/csv/'

CSV_PATH = CSV_DIR_PATH + 'employers.csv'
CSV_PATH_TEST = CSV_DIR_PATH + 'test.csv'
CSV_PATH_5_2 = CSV_DIR_PATH + 'employers_5_2.csv'
NEXT_MONTH_CSV_PATH = CSV_DIR_PATH + 'employers-next.csv'

# Import from json
with open(JSON_DIR_PATH + 'employers_shift.json', 'r', encoding='utf-8') as shift_json:
    working_shift = json.load(shift_json)

with open(JSON_DIR_PATH + 'employers_month.json', 'r', encoding='utf-8') as month_json:
    months = json.load(month_json)

with open(JSON_DIR_PATH + 'employers_info.json', 'r', encoding='utf-8') as info_json:
    employers_info = json.load(info_json)


