import cherrypy
import ipaddress
import telebot

class WebhookServer(object):
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot
        self.trusted_subnet_list = [
            ipaddress.ip_network('149.154.160.0/20'),
            ipaddress.ip_network('91.108.4.0/22')
        ]
    
    def is_trusted(self, current_ip):
        try:
            for current_subnet in self.trusted_subnet_list:
                if ipaddress.ip_address(current_ip) not in current_subnet:
                    print(current_subnet, current_ip)
                    print('Not checked!')
                    raise cherrypy.HTTPError(403, "Forbidden")
            return True
        except cherrypy.CherryPyException:
            return False

    @cherrypy.expose
    def index(self):
        print(cherrypy.request)
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
