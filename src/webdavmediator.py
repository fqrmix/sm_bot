from dataclasses import dataclass
from secrets import choice
from string import ascii_letters, digits
from sm_bot.services.logger import logger

@dataclass
class WebDavUserData:
    password: str
    telegram: str

    def get_string(self):
        return f"{self.telegram}:{self.password}"

class WebDavMediator:
    USER_DATA_PATH = './sm_bot/src/sm_bot/data/webdav'

    def __init__(self, user) -> None:
        self.user = user
        self.userdata = self._generate_userdata()

    def push_user_to_webdav_server(self):
        with open(self.USER_DATA_PATH + '/users', "r", encoding='utf-8') as users_file:
            current_file = users_file.read()

        if not self.userdata.telegram in current_file:
            with open(self.USER_DATA_PATH + '/users', "a", encoding='utf-8') as users_file:
                users_file.write('\n' + self.userdata.get_string())
            
            logger.info(f'[webdav-mediator] {self.userdata} was successfully appended to users file')
        else:
            logger.warn(f'[webdav-mediator] {self.user.telegram} already exist in webdav users file')


    def _generate_userdata(self) -> WebDavUserData:
        return WebDavUserData(
            password=self._generate_password(),
            telegram=self.user.telegram
        )
    
    @staticmethod
    def _generate_password() -> str:
        alphabet = ascii_letters + digits
        return ''.join(choice(alphabet) for i in range(20))