from microdot_asyncio import Microdot,  send_file
import machine
import uasyncio
import time
import sys
import network
import os
from iotwifi import IOTwifi


import relay
import sensor
from history import History
from gardensettings import GardenSettings
from logger import Logger

print("mainloop")
iotwifi = IOTwifi(False)
lastTime = time.time()
app = Microdot()
gardenSettings = GardenSettings()
wlan = network.WLAN(network.STA_IF)

def getFreespaceKB():
    stat = os.statvfs("/")
    free = stat[0] * stat[3]
    return free / 1024


async def clockWatcher():
    try:
        global lastTime
        while True:
            if not wlan.isconnected():
                # restart if we lose network connection
                print("wlan.isconnected()", wlan.isconnected(),
                      "wlan.status()", wlan.status())
                with open("error.txt", "a") as errFile:
                    errFile.write("\n" + str(time.localtime()) + "\n")
                    errFile.write(
                        "Network connection lost - status=" + str(wlan.status()) + "\n")
                print("Network connection lost, rebooting in 5 seconds...")
                time.sleep(5)
                machine.reset()
            # Update pump and cam time tracking
            if relay.getPump() == "on":
                sensor.pumpSeconds += 60
            if relay.getCam() == "on":
                sensor.camMinutes += 1
            # Check if the pump or cam should be turned off
            relay.checkToTurnOff()
            # Check if the pump should be turned on
            relay.checkToTurnOn()
            # Check if it is a new hour and time to log sensor data
            lastHour = time.localtime(lastTime)[3]
            currentHour = time.localtime()[3]
            if lastHour != currentHour:
                # New hour
                if getFreespaceKB() < gardenSettings.getMinFreeKB:
                    #  Remove oldest log
                    oldestLog = "zzzzzzzzzzzzzzz"
                    for filename in os.listdir("/log"):
                        print(filename,oldestLog)
                        if filename < oldestLog:
                            oldestLog = filename
                    if oldestLog != "zzzzzzzzzzzzzzz":
                        os.remove("/log/" + oldestLog)
                # Send data to iot
                sensorData = sensor.getSensors()
                iotwifi.sendClimate(sensorData["temprature"],sensorData["humidity"])
                iotwifi.sendGarden(sensorData["sm1"],sensorData["sm2"],sensorData["waterLevel"],sensorData["pump"],sensorData["cam"],sensorData["battery"])
                # Save data locally
                sensor.writeLog()

                relay.checkToTurnOnForMoisture()
            lastTime = time.time()
            # sleep for 60 seconds
            await uasyncio.sleep(60)
    except Exception as e:
        logger = Logger()
        logger.writeException(e)
        print("Clock watcher exception, rebooting in 5 seconds...")
        time.sleep(5)
        machine.reset()

# Get list of errors
@app.route('/log')
def getSysLog(request):
    logger = Logger()
    return logger.getLog(), 200,  {'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/html'}


@app.route('/log/clear')
def clearSysLog(request):
    logger = Logger()
    logger.clearLog()
    return "", 200,  {'Access-Control-Allow-Origin': '*', 'Content-Type': 'text/html'}

# Turn the pump on or off
@app.route('/pump')
def getPump(request):
    return {'pump': relay.getPump()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/pump/<setting>')
def pump(request, setting):
    if setting == 'on':
        relay.pumpOn()
        return {'pump': relay.getPump()}, 200, {'Access-Control-Allow-Origin': '*'}
    if setting == 'off':
        relay.pumpOff()
        return {'pump': relay.getPump()}, 200,  {'Access-Control-Allow-Origin': '*'}
    return "Not Found", 404

#  turn the webcam on or off
@app.route('/cam')
def getCam(request):
    return {'cam': relay.getCam()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/cam/<setting>')
def cam(request, setting):
    if setting == 'on':
        relay.camOn()
        return {'cam': relay.getCam()}, 200, {'Access-Control-Allow-Origin': '*'}
    if setting == 'off':
        relay.camOff()
        return {'cam': relay.getCam()}, 200,  {'Access-Control-Allow-Origin': '*'}
    return "Not Found", 404

#  Get current sensor readings
@app.route('/sensors')
def sensors(request):
    return {'sensors': sensor.getSensors()}, 200,  {'Access-Control-Allow-Origin': '*'}

# Retrieve log data
@app.route("/history/<start>/<end>")
@app.route("/history/<start>")
@app.route("/history")
def gardenHistory(request, start=0, end=0):
    # Check the start and end values are integers
    try:
        _start = int(start)
        _end = int(end)
    except:
        return "Start/End values not integer(s).", 400,  {'Access-Control-Allow-Origin': '*'}
    if start == 0:
        start = time.time() - (24 * 60 * 60)
    if end == 0:
        end = time.time()
    history = History()
    return history.getLogData(int(start), int(end)), 200,  {'Access-Control-Allow-Origin': '*'}

# Setters and getters for settings
@app.route('/settings/pumpOnSeconds')
def getPumpOnSeconds(request):
    return {"pumpOnSeconds": gardenSettings.getPumpOnSeconds()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpOnSeconds/<int:value>')
def setPumpOnSeconds(request, value):
    return {"pumpOnSeconds": gardenSettings.setPumpOnSeconds(value)}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/camOnMinutes')
def getCamOnMinutes(request):
    return {"camOnMinutes": gardenSettings.getCamOnMinutes()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/camOnMinutes/<int:value>')
def setCamOnMinutes(request, value):
    return {"camOnMinutes": gardenSettings.setCamOnMinutes(value)}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpMSTriggerOn')
def getPumpOnSeconds(request):
    return {"pumpMSTriggerOn": gardenSettings.getPumpMSTriggerOn()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpMSTriggerOn/<int:value>')
def setPumpMSTriggerOn(request, value):
    return {"pumpMSTriggerOn": gardenSettings.setPumpMSTriggerOn(value)}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpMSBlock')
def getPumpMSBlock(request):
    return {"pumpMSBlock": gardenSettings.getPumpMSBlock()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpMSBlock/<int:value>')
def setPumpMSBlock(request, value):
    return {"pumpMSBlock": gardenSettings.setPumpMSBlock(value)}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpTimes')
def getPumpTimes(request):
    return {"pumpTimes": gardenSettings.getPumpTimes()}, 200,  {'Access-Control-Allow-Origin': '*'}


@app.route('/settings/pumpTimes/<value>')
def setPumpTimes(request, value):
    return {"pumpTimes": gardenSettings.setPumpTimes(value)}, 200,  {'Access-Control-Allow-Origin': '*'}


# Get all settings at once ( save some network time )
@app.route('/settings')
def getAllSettings(request):
    settings = {"pumpTimes": gardenSettings.getPumpTimes(),
                "pumpOnSeconds": gardenSettings.getPumpOnSeconds(), "camOnMinutes": gardenSettings.getCamOnMinutes(),
                "pumpMSTriggerOn": gardenSettings.getPumpMSTriggerOn(), "pumpMSBlock": gardenSettings.getPumpMSBlock()}
    return settings, 200,  {'Access-Control-Allow-Origin': '*'}

#  All other request return static files from garden_ui folder
@app.route('/')
def index(request):
    return send_file('garden-ui/index.html', compressed=True)


@app.route('/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        # print("directory traversal is not allowed " + path)
        return 'Not found', 404
    # print(path)
    return send_file('garden-ui/' + path, compressed=True)



logger = Logger()
logger.writeLogLine("*** Restart ***")
# Fire up background co-routine first
uasyncio.create_task(clockWatcher())
try:
    # Fire up the microDot server (also runs as a background coroutine)
    # Note: debug requires a terminal connection so turn of when running in garden from battery
    app.run(debug=False, port=80)
except:
    logger.writeLogLine("microDot Exception")
    print("Microdot exception, restarting in 5 seconds...")
    time.sleep(5)
    machine.reset()
