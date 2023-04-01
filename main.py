import relay
from microdot_asyncio import Microdot,  send_file, Response
import uasyncio
import sensor
import time

import machine
import time
led = machine.Pin("LED", machine.Pin.OUT)
lastTime = time.time()


led.off()

app = Microdot()


# async def blink():
#     while True:
#         led.on()
#         await uasyncio.sleep(1)
#         led.off()
#         await uasyncio.sleep(1)


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
        print("lastTime:", time.localtime(lastTime))
        # sleep for 60 seconds
        await uasyncio.sleep(60)


@app.route('/pump')
def pumpValue(request):
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
