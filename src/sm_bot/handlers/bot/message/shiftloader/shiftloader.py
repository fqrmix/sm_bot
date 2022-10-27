from ast import Raise
import datetime
from sm_bot.handlers.workersmanager.employees import Employees
from sm_bot.services.webdav import WebDAV
from sm_bot.services.logger import logger
from sm_bot.services.bot import bot
from sm_bot.config import config
from telebot import types, TeleBot

# Loading .csv file
def handle_shift_loader(message: types.Message, bot: TeleBot):
    '''
        Telegram handler of command /load, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        employer_name, value = Employees.get_employer_name(
            val = message.from_user.username,
            parameter = "telegram",
            my_dict = config.employers_info)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для"\
                    "сотрудников тех. сопровождения/подключения!"
            )
            error_msg = f"[load] User @{message.from_user.username} use command /load in chatID "\
                f"- {message.chat.id}, chatName - {message.chat.title}, but he doesn't exist in employers database!"
            raise ValueError(error_msg)
        else:
            logger.info(f'[load] User "{message.from_user.username}" trying to load a new CSV file')
            link_message = bot.send_message(
                        chat_id = message.chat.id,
                        text = 'Пришли мне файл с графиком в формате .CSV на следующий месяц')
            bot.register_next_step_handler(link_message, load_employers_csv)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

def load_employers_csv(message: types.Message):
    '''
        Continiuous function of load handler.
    '''
    if message.content_type != 'document':
        if message.text == "/cancel":
            bot.send_message(message.chat.id, "Loading was canceled by user")
            logger.info(f"[load] Loading was canceled by user @{message.from_user.username}")
        else:
            bot.send_message(message.chat.id, f"I am waiting for CSV file!\n"\
                f"Not for {message.content_type}!\nUse /cancel command to quit")
            bot.register_next_step_handler(message, load_employers_csv)
    else:
        try:
            file_info = bot.get_file(message.document.file_id)
            if not file_info.file_path.endswith('.csv'):
                raise Exception('[load] Для загрузки допустимы только файлы с форматом .csv (разделитель запятая)')
            else:
                downloaded_file = bot.download_file(file_info.file_path)
                with open(config.NEXT_MONTH_CSV_PATH, 'wb') as csv_file:
                    csv_file.write(downloaded_file)
                bot.reply_to(message, "График на следующий месяц загружен!")
                logger.info("[load] График на следующий месяц загружен!")
                current_month = datetime.date.today().month
                next_month = current_month + 1 if current_month != 12 else 1
                WebDAV(config.NEXT_MONTH_CSV_PATH).generate_calendar(month=next_month)
            
        except Exception as error:
            bot.send_message(
                chat_id=message.chat.id,
                text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
                parse_mode='markdown'
            )
            logger.error(error, exc_info = True)
