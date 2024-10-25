# boot.py -- run on boot-up

import network
import ntptime
import time
import machine
from iotwifi import IOTwifi
# import ntptime_das


# ssid = 'spikeNG24_EXT'
# password = 'somerville885'

led = machine.Pin("LED", machine.Pin.OUT)
led.on()

iotwifi = IOTwifi(False)
iotwifi.connect()

time.sleep(2)
# Short delay before getting ntp time
# There is a known timing bug with this so try again
# if it fails.
try:
    ntptime.host = "snas.home"
    print(ntptime.host)
    ntptime.timeout = 2
    ntptime.settime()
except:
    print("ntptime error! Rebooting...")
    time.sleep(1)
    machine.reset()

print("UMT time：%s" % str(time.localtime()))
for x in range(0, 10):
    # Quick flash to indicate we are connected
    time.sleep(.05)
    led.on()
    time.sleep(.05)
    led.off()

import mainLoop

