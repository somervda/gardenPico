import os
from machine import Pin, ADC, I2C
import time
import bme280

pumpSeconds = 0
camMinutes = 0

# Dropped freq to 20K, original 400K was to fast to get humidity from BME280
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=20000)

sm1ADC = ADC(26)
sm2ADC = ADC(27)
batADC = ADC(28)
wetVolts = 1.1
dryVolts = 2.6


def file_or_dir_exists(filename):
    try:
        os.stat(filename)
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


def makeLogLine():
    global pumpSeconds
    global camMinutes
    logLine = str(time.time()) + ","
    logLine += str(getWetness(sm1ADC)) + "," + \
        str(getWetness(sm2ADC)) + "," + str(getBattery(batADC)) + ","
    logLine += str(getTemperature()) + "," + str(getHumidity()) + ","
    logLine += str(pumpSeconds) + "," + str(camMinutes) + "\n"
    pumpSeconds = 0
    camMinutes = 0
    return logLine


def writeLog():
    logMonth = str(time.localtime()[1])
    if len(logMonth) == 1:
        logMonth = "0" + logMonth
    logDay = str(time.localtime()[2])
    if len(logDay) == 1:
        logDay = "0" + logDay
    logName = "/log/" + str(time.localtime()[0]) + logMonth + logDay + ".csv"
    logLine = makeLogLine()
    print(logName, logLine)
    if file_or_dir_exists(logName):
        # Add log details to existing file
        with open(logName, "a") as logFile:
            logFile.write(logLine)
    else:
        with open(logName, "w") as logFile:
            logFile.write(logLine)


def read():
    for x in range(30):
        print(x, getWetness(sm1ADC), getWetness(sm2ADC), getBattery(batADC))
        time.sleep(1)
