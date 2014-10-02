import sys
from datetime import datetime

class Logger():
	def __init__(self,out=sys.stdout):
		self.out = out
		
	def info(self,message):
		self.message(datetime.now().strftime("%Y-%m-%d %H:%M ") + message)
		
	def message(self,message):
		self.out.write(message + '\n')