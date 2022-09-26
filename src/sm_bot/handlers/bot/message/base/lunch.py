from telebot import types, TeleBot
from sm_bot.services.logger import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class LunchQuery:
    def __init__(self) -> None:
        self.messages = list()
        self.lunch_list = list()

    # Send lunch poll
    def send_lunch_query(self, chat_id, bot: TeleBot) -> None:
        '''
            Function that send lunch poll to Telegram Chat.
            _______
            Arguments:
                *chat_id == Id of Telegram Chat
        '''
        try:
            message = bot.send_poll(
                chat_id = chat_id,
                question = 'Доброе утро!\nВо сколько обед?',
                is_anonymous = False,
                options = ['11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'])
            logger.info(f'[lunch-poll] Lunch poll has been successfully sent into chatID: {chat_id}!')
            self.messages.append(message.json)
        except Exception as error:
            logger.error(error, exc_info = True)
    
    def update_markup(self, bot: TeleBot) -> None:
        for message in self.messages:
            bot.edit_message_reply_markup(
                    chat_id=message['chat']['id'],
                    message_id=message['message_id'],
                    reply_markup=self.build_keyboard()
                )

    def create_buttons(self) -> list:
        buttons_list = list()
        for obj in self.lunch_list:
            current_button = InlineKeyboardButton(
                text=f"{obj['name']} | {obj['lunch_time']}", 
                callback_data='lunch_query')
            buttons_list.append(current_button)
        return buttons_list

    def build_keyboard(self) -> InlineKeyboardMarkup:
            keyboard = InlineKeyboardMarkup(row_width = 2)
            buttons_list = self.create_buttons()
            keyboard.add(*buttons_list)
            return keyboard

lunchquery = LunchQuery()

# Repeat lunch poll
def handle_lunch(message: types.Message, bot: TeleBot) -> None:
    '''
        Telegram handler of command /lunch, which loading CSV file for next month.
        _______
        Arguments:
            *message == Object of message
    '''
    try:
        lunchquery.send_lunch_query(message.chat.id, bot)
    except Exception as error:
        bot.send_message(
            chat_id=message.chat.id,
            text='Во время обработки запроса произошла ошибка! Необходимо проверить логи.',
            parse_mode='markdown'
        )
        logger.error(error, exc_info = True)

