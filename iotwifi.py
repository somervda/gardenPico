# Module used to send iot data to my iot server

import network
import machine
import time
from gardensettings import GardenSettings
import requests
import json

class IOTwifi:

    quiet = True
    wifi = None
    led = machine.Pin("LED", machine.Pin.OUT)
    settings = None


    def __init__(self,quiet=True):
        not self.quiet and print('__init__',quiet)
        self.quiet = quiet
        self.settings = GardenSettings()

    def ledFlash(self):
        self.led.on()
        time.sleep(0.08)
        self.led.off()
        time.sleep(0.1)
        self.led.on()
        time.sleep(0.08)
        self.led.off()
        time.sleep(0.8)

    def connect(self):
        self.wlan = network.WLAN(network.STA_IF)
        not self.quiet and print("Connecting to " + self.settings.getSSID() + ":")
        self.wlan.active(True)
        # Note SSID is case sensitive i.e. make sure it is gl24 not GL24
        # 0   STAT_IDLE -- no connection and no activity,
        # 1   STAT_CONNECTING -- connecting in progress,
        # -3  STAT_WRONG_PASSWORD -- failed due to incorrect password,
        # -2  STAT_NO_AP_FOUND -- failed because no access point replied,
        # -1  STAT_CONNECT_FAIL -- failed due to other problems,
        # 3   STAT_GOT_IP -- connection successful.
        not self.quiet and print("hostname:",self.settings.getHostname())
        network.hostname(self.settings.getHostname())
        self.wlan.connect(self.settings.getSSID(), self.settings.getPassword())
        connectCount = 0
        while not self.wlan.isconnected() and  self.wlan.status() != 3:
            connectCount+=1
            if connectCount>30:
                not self.quiet and print(" wifi connect timed out. status:", self.wlan.status() )
                self.powerOff()
                return False
            # Slow LED flash while connecting
            not self.quiet and print(".", end="")
            self.ledFlash()

        time.sleep(2)
        not self.quiet and print("Connected! ifconfig:",self.wlan.ifconfig()[0],self.wlan.ifconfig()[1],self.wlan.ifconfig()[2],self.wlan.ifconfig()[3])
        return True

    def send(self,iotData):
        not self.quiet and print("wifi send iotData:",iotData)
        self.ledFlash()
        # Add user and device_id to the iotData
        iotData["user"] = self.settings.getIotUser()
        iotData["deviceID"] = self.settings.getDEVICE_ID()
        iotData["sensorTimestamp"] = time.time()
        not self.quiet and print("iotData:",iotData)
        url = url = 'http://' + self.settings.getIotHost() + ':' + str(self.settings.getIotPort()) + \
        '/write?iotData=' + json.dumps(iotData).replace("\'","\"").replace(" ","")


        try:
            not self.quiet and print("wifi send url:",url)
            resp = requests.get(url)
            not self.quiet and print("wifi send status:",resp.status_code)
            if resp.status_code==200:
                return True
            else:
                not self.quiet  and print('Fail Response:')
                return False
        except Exception as error:
            # handle the exception
            not self.quiet  and print("A wifi exception occurred:", error)
            return False

    def powerOff(self):
        not self.quiet and print("iotwifi power off")
        self.wlan.disconnect()
        self.wlan.active(False)
        self.wlan.deinit()

    def sendClimate(self, celsius, humidity):
        iotData = {}
        iotData["celsius"] = celsius
        iotData["humidity"] = humidity
        iotData["appID"] = self.settings.getCLIMATE_ID()
        self.send(iotData)

    def sendGarden(self, moisture1, moisture2,waterLevel,pumpSeconds,camSeconds,houseVolts):
        iotData = {}
        iotData["moisture1"] = moisture1
        iotData["moisture2"] = moisture2
        iotData["waterLevel"] = waterLevel
        iotData["pumpSeconds"] = pumpSeconds
        iotData["camSeconds"] = camSeconds
        iotData["houseVolts"] = houseVolts
        iotData["appID"] = self.settings.getGARDEN_ID()
        self.send(iotData)

