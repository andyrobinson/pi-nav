
class SelfTest():

    def __init__(self,red_led,green_led,timer,rudder,rudder_min_angle,rudder_max_angle):
        self.red_led = red_led
        self.green_led = green_led
        self.timer = timer
        self.rudder = rudder
        self.rudder_min_angle = rudder_min_angle
        self.rudder_max_angle = rudder_max_angle

    def run(self):
        self.with_led_blink(self.red_led,self.rudder_test)
        self.test_complete()

    def rudder_test(self):
        self.rudder.set_position(self.rudder_min_angle)
        self.timer.wait_for(0.2)
        self.rudder.set_position(self.rudder_max_angle)
        self.timer.wait_for(0.2)
        self.rudder.set_position(0)

    def with_led_blink(self,led,method):
        led.high()
        self.timer.wait_for(0.5)
        method()
        led.low()
        self.timer.wait_for(0.5)

    def test_complete(self):
        self.with_led_blink(self.green_led,lambda:None)
