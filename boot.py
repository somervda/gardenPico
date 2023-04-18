# boot.py -- run on boot-up

import network
import ntptime
import time
import machine


ssid = 'guest24'
password = 'backyard'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected() and wlan.status() >= 0:
    wlan.ifconfig(('192.168.1.40', '255.255.255.0',
                   '192.168.1.1', '8.8.8.8'))
    wlan.connect(ssid, password)
    print("Connecting:")
    while not wlan.isconnected() and wlan.status() >= 0:
        print(".", end="")
        time.sleep(1)

print("Connected! IP Address = " + wlan.ifconfig()[0])
# Short delay before getting ntp time
# There is a known timing bug with this so try again
# if it fails.
time.sleep(2)
try:
    ntptime.settime()
except:
    print("ntptime error! Rebooting...")
    time.sleep(1)
    machine.reset()

print("UMT time：%s" % str(time.localtime()))
