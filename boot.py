# boot.py -- run on boot-up

import network
import ntptime
import time
import machine


ssid = 'guest24'
password = 'backyard'

led = machine.Pin("LED", machine.Pin.OUT)
led.on()


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected() and wlan.status() >= 0:
    wlan.ifconfig(('192.168.1.40', '255.255.255.0',
                   '192.168.1.1', '8.8.8.8'))

    wlan.connect(ssid, password)

    print("Connecting:")
    while not wlan.isconnected() and wlan.status() >= 0:
        # Slow flas while connecting
        print(".", end="")
        led.off()
        time.sleep(0.5)
        led.on()
        time.sleep(.5)

time.sleep(.5)
print("Connected! IP Address = " + wlan.ifconfig()[0])
# Short delay before getting ntp time
# There is a known timing bug with this so try again
# if it fails.
try:
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
