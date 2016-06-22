# removes need for messing with sudo or permissions
import os
import time
os.system("gpio -g mode 17 out")
os.system("gpio -g mode 18 out")
os.system("gpio -g write 17 1")
time.sleep(2)
os.system("gpio -g write 17 0")
os.system("gpio -g write 18 1")
time.sleep(2)
os.system("gpio -g write 18 0")
