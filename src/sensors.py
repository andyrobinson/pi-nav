

class Sensors():
	def __init__(self,gps):
		self.gps = gps


	@property
	def hasfix(self):
		return self.gps.hasfix

	@property
	def position(self):
		return self.gps.position	

	@property
	def time(self):
		return self.gps.time

	@property
	def track(self):
		return self.gps.track

	@property
	def speed(self):
		return self.gps.speed	

	@property
	def track_error(self):
		return self.gps.track_error
	
	@property
	def speed_error(self):
		return self.gps.speed_error

