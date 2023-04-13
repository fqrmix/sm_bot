import cherrypy
import ipaddress
import telebot

class WebhookServer:
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot
        self.trusted_subnet_list = [
            ipaddress.ip_network('149.154.160.0/20'),
            ipaddress.ip_network('91.108.4.0/22')
        ]
    
    def is_trusted(self, current_ip):
        for current_subnet in self.trusted_subnet_list:
            if ipaddress.ip_address(current_ip) in current_subnet:
                return True
        raise cherrypy.HTTPError(403, "Forbidden")

    @cherrypy.expose
    def index(self):
        try:
            remote_ip = cherrypy.request.remote.ip
            if self.is_trusted(remote_ip):
                print('IP is trusted!')
                length = int(cherrypy.request.headers['content-length'])
                json_string = cherrypy.request.body.read(length).decode("utf-8")
                update = telebot.types.Update.de_json(json_string)
                self.bot.process_new_updates([update])
                return ''
        except cherrypy.CherryPyException:
            raise cherrypy.HTTPRedirect("https://fqrmix.ru")

