# -*- coding: utf-8 -*-
from message import Message, MS_TYPE_COMMAND
from utils import out

from image.img import Img
from image.imgs import Imgs
from image.utils import thinning
from neural_network.layer_fc import LayerFC
from neural_network.neural_network import NeuralNetwork, nn_load

class Manager(object):
	name = 'manager'

	def __init__(self):
		self.socket = None

	def connected(self, socket):
		self.socket = socket

	def disconnected(self):
		self.socket = None

	def interaction(self, in_message=None):
		MS = Message(in_message, self.socket)
		out('Manager recieved a message:',MS)
		if not MS.act(self):
			self.stop(MS)

	def get_info(self, MS):
		print 'get_info'

	def solve_captcha(self, MS):
		#Im = Img(url=MS.params['captcha_url'])
		#Im.show()
		print MS.params['captcha_url']
		

		result = u'2323'
		self.send_solution(MS, result)

	def send_solution(self, MS, result):
		MS.type = MS_TYPE_COMMAND
		MS.action = 'write_solution'
		MS.params = {'captcha_text': result}
		MS.send(self.socket)

	def stop(self, MS=None):
		out('Manager work is stopped.')