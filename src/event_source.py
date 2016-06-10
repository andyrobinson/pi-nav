import sys
from events import Event,EventName

class EventSource:

    def __init__(self,exchange,timer,logger,config):
        self.logger = logger
        self.timer = timer
        self.exchange = exchange
        self.ticking = True
        self.config = config
        exchange.subscribe(EventName.end,self.finish)

    def start(self):
        self._safely(self._signal_start)

        while self.ticking:
            self._safely(self._tick)
            self.timer.wait_for(self.config['tick interval'])

    def finish(self,event):
        self.ticking = False

    def _safely(self,method):
        try:
            method()
        except:
            try:
                etype,e,traceback = sys.exc_info()
                self.logger.error('EventSource, {0}: {1}'.format(etype.__name__,', '.join(str(x) for x in e.args)))
            except:
                pass

    def _signal_start(self):
        self.exchange.publish(Event(EventName.start))

    def _tick(self):
        self.exchange.publish(Event(EventName.tick))
