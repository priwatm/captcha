# -*- coding: utf-8 -*-
MS_TYPE_COMMAND = 'command'
MS_TYPE_RESULTS = 'results'
MS_TYPE_ERROR   = 'error'

import json

from utils import out

class Message(object):

	def __init__(self, s=None, socket=None):
		if isinstance(s, basestring) and len(s)>0:
			s = json.loads(s)
		if not isinstance(s, dict):
			s = {}
		self.source  = s.get('source')
		self.url     = s.get('url')
		self.type    = s.get('type')
		self.action  = s.get('action')
		self.params  = s.get('params', {})
		self.results = s.get('results', [])
		self.socket  = socket

	@property
	def to_dict(self):
		s = {'source': self.source, 'url': self.url, 'type': self.type, 
		     'action': self.action, 'params': self.params, 'results': self.results}
		return s

	@property
	def to_send(self):
		self.source = 'server'
		self.url = 'localhost'
		if self.type != MS_TYPE_COMMAND:
			self.action = None
		if self.type != MS_TYPE_RESULTS:
			self.results = []
		if self.type == MS_TYPE_RESULTS:
			self.params = {}
		return self.to_dict #json.dumps(s)

	def act(self, obj):
		if self.type == MS_TYPE_ERROR:
			error = self.params['error']
			mess  = 'JS ERROR (in %s.%s): %s'%(error['cl'], error['func'], error['text'])
			raise ValueError(mess)
		if self.type != MS_TYPE_COMMAND or not self.action:
			return False
		function = obj.__getattribute__(self.action)
		if function:
			out('Action "%s" from "%s" will be performed (command).'%(self.action, obj.name)) 
			function(self); return True
		return False

	def send(self, socket='None'):
		if socket != 'None':
			self.socket = socket
		if not self.socket:
			raise ValueError('Can not send message: socket is not set.')
		out('Message will be sent:', self)
		self.socket.write(self.to_send)

	def __unicode__(self):
		s = 'MESSAGE '
		s+= '> %-10s '%('%-s'%self.source if self.source else 'SOURCE')
		s+= '> %-10s '%('%-s'%self.type if self.type else 'TYPE')
		s+= '> %-20s '%('%-s'%self.action if self.action else '')
		s+= '\nurl     >>>\n             %s\n'%self.url if self.url else ''
		s+= '\nparams  >>>\n             %s\n'%unicode(self.params) if self.params else ''
		s+= '\nresults >>>\n             %s\n'%unicode(self.results) if self.results else ''
		return s

	def __str__(self):
		return self.__unicode__().encode('utf-8')