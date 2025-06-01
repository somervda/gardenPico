import machine
from gardensettings import GardenSettings
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
    gs = GardenSettings()
    # Check there is enough water to pump before starting irrigation
    if (sensor.getWaterLevel() > 1):
        if (checkForMoistureBlock()):
            print("Garden is already moist, skip pump")
        else:
            # Fire up the pump
            pumpRelay.on()
            pumpValue = "on"
            pumpOffTime = time.time() + gs.getPumpOnSeconds()
    else:
        print("Water level too low, pump not started", sensor.getWaterLevel())


def pumpOff():
    global pumpValue
    pumpRelay.off()
    pumpValue = "off"


def getPump():
    global pumpValue
    return pumpValue


def camOn():
    global camValue, camOffTime
    gs = GardenSettings()
    camRelay.on()
    camValue = "on"
    camOffTime = time.time() + (gs.getCamOnMinutes() * 60)
    # print("CamOffTime:", camOffTime)


def camOff():
    global camValue
    camRelay.off()
    camValue = "off"


def getCam():
    global camValue
    return camValue


def checkToTurnOff():
    global pumpOffTime, camOffTime
    gs = GardenSettings()
    if (sensor.getWaterLevel() == 1):
        # print("water level is low, turned off pump")
        pumpOff()
    if pumpOffTime is None:
        if getPump() == "on":
            pumpOff()
    else:
        if pumpOffTime < time.time():
            pumpOff()
            pumpOffTime = None
    # print("camOffTime:", camOffTime, "time.time():", time.time())
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
    # moisture sensors say pump should be turned on, only check once an hour
    gs = GardenSettings()
    if sensor.getWetness(sensor.sm1ADC) < gs.getPumpMSTriggerOn() or sensor.getWetness(sensor.sm2ADC) < gs.getPumpMSTriggerOn():
        print("Pump on , low moisture")
        pumpOn()

def checkForMoistureBlock():
    # Check if garden moisture is greater than the Block value (Will not water in that case)
    gs = GardenSettings()
    print("checkForMoistureBlock (sm1,sm2,block value):", sensor.getWetness(sensor.sm1ADC),sensor.getWetness(sensor.sm2ADC),gs.getPumpMSBlock() )
    if sensor.getWetness(sensor.sm1ADC) > gs.getPumpMSBlock() and sensor.getWetness(sensor.sm2ADC) > gs.getPumpMSBlock():
        print("Moisture is higher than block value (Dont pump)")
        return True
    else:
        print("Moisture is lower or equal to block value (Pump)")
        return False
