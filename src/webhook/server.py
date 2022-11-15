import cherrypy
import ipaddress
import telebot

class WebhookServer(object):
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    @cherrypy.expose
    def index(self):
        print(cherrypy.request)
        try:
            remote_ip = cherrypy.request.remote.ip
            if ipaddress.ip_address(remote_ip) not in ipaddress.ip_network('149.154.160.0/20') \
                and ipaddress.ip_address(remote_ip) not in ipaddress.ip_network('91.108.4.0/22'):
                raise cherrypy.HTTPError(403, "Forbidden")
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            self.bot.process_new_updates([update])
            return ''
        except cherrypy.CherryPyException:
            raise cherrypy.HTTPRedirect("https://fqrmix.ru")