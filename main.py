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


# wlan = network.WLAN(network.STA_IF)
# print("Connecting to " + ssid + ":")
# wlan.active(True)
# wlan.ifconfig(('192.168.1.40', '255.255.255.0',
#                '192.168.1.1', '192.168.1.1'))
# wlan.connect(ssid, password)
# while not wlan.isconnected() and wlan.status() >= 0:
#     # Slow LED flash while connecting
#     print(".", end="")
#     led.off()
#     time.sleep(0.5)
#     led.on()
#     time.sleep(.5)
iotwifi = IOTwifi(False)
iotwifi.connect()

time.sleep(2)
print("Connected! IP Address = " + wlan.ifconfig()[0])
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
