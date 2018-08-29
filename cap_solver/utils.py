# -*- coding: utf-8 -*-
ONLY_WARNINGS = False

from datetime import datetime

def out(mess, obj=None, w=False):
	res = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	res+= ' | CAP-SOLVER : ' + unicode(mess)
	res+= '\n' + ' '*20 + '| ' + unicode(obj) if obj else ''
	if ONLY_WARNINGS and not w:
		return
	print res