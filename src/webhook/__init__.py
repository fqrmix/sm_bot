import cherrypy

cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 7771,
        'tools.proxy.on': True,
        'engine.autoreload.on': False
    })

print('Server inited')

