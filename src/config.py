
LOGGING_CRITICAL = 50
LOGGING_ERROR = 40
LOGGING_WARNING = 30
LOGGING_INFO = 20
LOGGING_DEBUG = 10
LOGGING_NOTSET = 0

CONFIG = {
    'helm' :          {'on course threshold': 20,
                       'turn on course min count': 5,
                       'on course check interval': 5,
                       'turn steer interval': 0.2},
    'steerer':        {'full rudder deflection': 30,
                       'ignore deviation below': 5,
                       'ignore rate of turn below': 10,
                       'rate of turn factor': 0.1},
    'sailing helm':   {'no go angle': 45,
                       'min tack duration': 5},
    'course steerer': {'sleep time' : 1},
    'navigator' :     {'min time to steer': 5,
                       'max time to steer': 600},
    'sensors' :       {'smoothing' : 5,
                       'compass smoothing':2,
                       'log interval': 10,
                       'update averages interval': 0.2},
    'event source' :  {'tick interval':0.1},
    'wiring' :        {'logging level': LOGGING_INFO}
    }
