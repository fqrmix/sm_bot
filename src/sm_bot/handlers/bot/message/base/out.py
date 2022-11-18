from telebot import types, TeleBot
from sm_bot.services.logger import logger
from sm_bot.config import config
from sm_bot.handlers.workersmanager.employees import Employees

# Out for lunch
def handle_out(message: types.Message, bot: TeleBot):
    '''
        Telegram handler of command /out, which send notification about employers goes for lunch,
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        employer_telegram_id = message.from_user.id
        employer_name, value = Employees.get_employer_name(
            val = str(employer_telegram_id),
            parameter = 'telegram_id',
            my_dict = config.Config.employers_info)
        if employer_name is None:
            bot.send_message(
                chat_id = message.chat.id,
                text = "Данная команда предназначена только для"\
                    "сотрудников тех. сопровождения/подключения!"
            )
            error_msg = f"[out] User @{message.from_user.username} use command /out in chatID - {message.chat.id}, "\
                f"chatName - {message.chat.title}, but he doesn't exist in employers database!"
            raise ValueError(error_msg)
        bot.send_message(
            chat_id = message.chat.id,
            parse_mode = "Markdown",
            text = f"[{employer_name}](tg://user?id={employer_telegram_id}) ушел(-ла) на обед."\
                f"\nРебята, подмените пожалуйста коллегу в чатах.")
        logger.info(f"[out] User @{message.from_user.username} successfully use command /out in "\
            f"chatID - {message.chat.id}, chatName - {message.chat.title}")
    except Exception as error:
        logger.error(error, exc_info = True)
