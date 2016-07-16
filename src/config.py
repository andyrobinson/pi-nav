import json
import os
current_path = os.path.dirname(os.path.abspath(__file__))

with open(current_path + '/config.json') as config_file:
    CONFIG = json.load(config_file)
