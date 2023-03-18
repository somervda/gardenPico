# boot.py -- run on boot-up

import network
import time

ssid = 'guest24'
password = 'backyard'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.ifconfig(('192.168.1.40', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
wlan.connect(ssid, password)
print("Connecting:")
while not wlan.isconnected() and wlan.status() >= 0:
    print(".", end="")
    time.sleep(1)

print("Connected! IP Address = " + wlan.ifconfig()[0])
