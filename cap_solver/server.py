# -*- coding: utf-8 -*-
SSL_OPTIONS = {'certfile': './../docs/cert.pem', 'keyfile': './../docs/key.pem'}
PORT = 443

import tornado.web
import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from manager import Manager
from utils import out

class Application(tornado.web.Application):

	def __init__(self):
		self.manager = Manager()
		handlers = [(r'/test', TestHandler),
		            (r'/capsolver/socket', SocketHandler)]
		settings = {'debug': True}
		super(Application, self).__init__(handlers, **settings)

class TestHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('Hello, world')

class SocketHandler(tornado.websocket.WebSocketHandler):

	def check_origin(self, origin):
		return True

	def open(self):
		out('WebSocket is opened.')
		self.application.manager.connected(self)

	def on_message(self, message):
		out('WebSocket recieved a message.')#\n>>> |%s|.\n'%message)
		self.application.manager.interaction(message)

	def on_close(self):
		out('WebSocket is closed.')
		self.application.manager.disconnected()

	def write(self, out_message):
		if not out_message:
			return
		out('WebSocket is going to send the message.')#\n>>> |%s|.\n'%out_message)
		self.write_message(out_message)

if __name__ == "__main__":
	app = Application()
	tornado.httpserver.HTTPServer(app, ssl_options=SSL_OPTIONS).listen(PORT)
	tornado.ioloop.IOLoop.instance().start()