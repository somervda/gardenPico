import machine
from settings import GardenSettings
import time
import sensor

pumpRelay = machine.Pin(15, machine.Pin.OUT)
pumpRelay.value(0)
pumpValue = "off"
pumpOffTime = None

camRelay = machine.Pin(14, machine.Pin.OUT)
camRelay.value(0)
camValue = "off"
camOffTime = None


def pumpOn():
    global pumpValue, pumpOffTime
    # Check there is enough water to pump before starting irrigation
    if (sensor.getWaterLevel() > 1):
        pumpRelay.on()
        pumpValue = "on"
        gs = GardenSettings()
        pumpOffTime = time.time() + gs.getPumpOnSeconds()
    else:
        print("Water level too low, pump not started", sensor.waterLevel)


def pumpOff():
    global pumpValue
    pumpRelay.off()
    pumpValue = "off"


def getPump():
    global pumpValue
    return pumpValue


def camOn():
    global camValue, camOffTime
    camRelay.on()
    camValue = "on"
    gs = GardenSettings()
    camOffTime = time.time() + (gs.getCamOnMinutes() * 60)


def camOff():
    global camValue
    camRelay.off()
    camValue = "off"


def getCam():
    global camValue
    return camValue


def checkToTurnOff():
    global pumpOffTime, camOffTime
    if (sensor.getWaterLevel() == 1):
        print("water level is low, turned off pump")
        pumpOff()
    if pumpOffTime is None:
        if getPump() == "on":
            pumpOff()
    else:
        if pumpOffTime < time.time():
            pumpOff()
            pumpOffTime = None
    if camOffTime is None:
        if getCam() == "on":
            camOff()
    else:
        if camOffTime < time.time():
            camOff()
            camOffTime = None


def checkToTurnOn():
    # Check to see if it is time to turn on the pump
    currentHour = time.localtime()[3]
    currentMinute = time.localtime()[4]
    militaryTime = (currentHour * 100) + currentMinute
    gs = GardenSettings()
    pumpTimes = (gs.getPumpTimes()).split(",")
    for pumpTime in pumpTimes:
        if int(pumpTime) == militaryTime:
            print("Pump on , timed:", militaryTime)
            pumpOn()


def checkToTurnOnForMoisture():
    gs = GardenSettings()
    # moisture sensors say pump should be turned on, only check once an hour
    if sensor.getWetness(sensor.sm1ADC) < gs.getPumpMSTriggerOn() or sensor.getWetness(sensor.sm2ADC) < gs.getPumpMSTriggerOn():
        print("Pump on , low moisture")
        pumpOn()
