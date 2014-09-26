import datetime

class App():
	def __init__(self,logger):
		self.logger = logger
		logger.info('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))