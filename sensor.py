import uos
from machine import Pin, ADC, I2C
import time
import bme280
import gc
from settings import GardenSettings
import relay

pumpSeconds = 0
camMinutes = 0

# Dropped freq to 20K, original 400K was to fast to get humidity from BME280
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=20000)

sm1ADC = ADC(26)
sm2ADC = ADC(27)
batADC = ADC(28)
wetVolts = 1.1
dryVolts = 2.6

waterLowPin = Pin(18, Pin.IN, Pin.PULL_UP)
waterMedPin = Pin(19, Pin.IN, Pin.PULL_UP)
waterHighPin = Pin(20, Pin.IN, Pin.PULL_UP)


def file_or_dir_exists(filename):
    try:
        uos.stat(filename)
        return True
    except OSError:
        return False


def getWetness(adc):
    smVolts = adc.read_u16() * (3.3 / 65536)
    wetness = int((1 - ((smVolts - wetVolts) / (dryVolts - wetVolts))) * 10)
    if wetness > 10:
        wetness = 10
    if wetness < 0:
        wetness = 0
    return wetness


def getBattery(adc):
    # Get the voltage at the ADC
    batADCVolts = adc.read_u16() * (3.3 / 65536)
    # Multiply by my resistor divider
    batVolts = batADCVolts * 6.423
    return round(batVolts, 1)


def getTemperature():
    bme = bme280.BME280(i2c=i2c)  # BME280 object created
    return bme.temperature


def getHumidity():
    bme = bme280.BME280(i2c=i2c)  # BME280 object created
    return bme.humidity


def getWaterLevel():
    # 4 water levels reported
    # 1- low (Don't pump), 2 - medium, 3 - medium/full, 4 - full
    if waterLowPin.value() == 0:
        return 1
    if waterMedPin.value() == 0:
        return 2
    if waterHighPin.value() == 0:
        return 3
    return 4


def makeLogLine():
    global pumpSeconds
    global camMinutes
    gs = GardenSettings()
    logLine = str(gs.getLocalTime()) + ","
    logLine += str(getWetness(sm1ADC)) + "," + \
        str(getWetness(sm2ADC)) + "," + str(getBattery(batADC)) + ","
    logLine += getTemperature().replace("C", "") + "," + \
        getHumidity().replace("%", "") + ","
    logLine += str(pumpSeconds) + "," + str(camMinutes)
    logLine += "," + str(getWaterLevel()) + "\n"
    pumpSeconds = 0
    camMinutes = 0
    return logLine


def getSensors():
    # Get a dictionary of sensor data and relay state
    sensors = {}
    sensors["sm1"] = getWetness(sm1ADC)
    sensors["sm2"] = getWetness(sm2ADC)
    sensors["battery"] = getBattery(batADC)
    sensors["temperature"] = float((getTemperature()).replace("C", ""))
    sensors["humidity"] = float((getHumidity()).replace("%", ""))
    sensors["waterLevel"] = getWaterLevel()
    # Also return memory details
    sensors["mem_free"] = gc.mem_free()
    sensors["file_bytes_free"] = (uos.statvfs("/")[0] * uos.statvfs("/")[3])
    sensors["file_bytes_total"] = (uos.statvfs("/")[0] * uos.statvfs("/")[2])
    sensors["pump"] = relay.getPump()
    sensors["cam"] = relay.getCam()
    print(sensors)
    return sensors


def writeLog():
    gs = GardenSettings()
    logMonth = str(time.localtime(gs.getLocalTime())[1])
    if len(logMonth) == 1:
        logMonth = "0" + logMonth
    logDay = str(time.localtime(gs.getLocalTime())[2])
    if len(logDay) == 1:
        logDay = "0" + logDay
    logName = "/log/" + \
        str(time.localtime(gs.getLocalTime())
            [0]) + logMonth + logDay + ".csv"
    logLine = makeLogLine()
    print(logName, logLine)
    if file_or_dir_exists(logName):
        # Add log details to existing file
        with open(logName, "a") as logFile:
            logFile.write(logLine)
    else:
        with open(logName, "w") as logFile:
            logFile.write(logLine)
