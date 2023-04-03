from microdot_asyncio import Microdot,  send_file
import machine
import uasyncio
import time


import relay
import sensor
from history import History
from settings import GardenSettings


lastTime = time.time()
app = Microdot()
gardenSettings = GardenSettings()


async def clockWatcher():
    global lastTime
    while True:
        # Update pump and cam time tracking
        if relay.getPump() == "on":
            print("Pump ON", sensor.pumpSeconds)
            sensor.pumpSeconds += 60
        if relay.getCam() == "on":
            print("Cam ON", sensor.camMinutes)
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
            sensor.writeLog()
            relay.checkToTurnOnForMoisture()
        lastTime = time.time()
        # sleep for 60 seconds
        await uasyncio.sleep(60)

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
        return "Start/End values not integer(s).", 400
    if start == 0:
        start = (time.time() - (24 * 60 * 60))
    if end == 0:
        end = time.time()
    history = History()
    return history.getLogData(int(start), int(end))

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
    return send_file('garden-ui/index.html')


@app.route('/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        # print("directory traversal is not allowed " + path)
        return 'Not found', 404
    # print(path)
    return send_file('garden-ui/' + path)


if __name__ == '__main__':
    # Fire up background coroutine first
    uasyncio.create_task(clockWatcher())
    try:
        # Fire up the microDot server (also runs as a background coroutine)
        app.run(debug=True, port=80)
    except:
        print("app.shutdown")
        app.shutdown()
