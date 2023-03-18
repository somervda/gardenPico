import relay
from microdot_asyncio import Microdot,  send_file, Response

app = Microdot()


@app.route('/pump')
def pumpValue(request):
    return {'pump': relay.getPump()}


@app.route('/pump/<setting>')
def pump(request, setting):
    if setting == 'on':
        relay.pumpOn()
        return {'pump': relay.getPump()}
    if setting == 'off':
        relay.pumpOff()
        return {'pump': relay.getPump()}
    return "Not Found", 404


if __name__ == '__main__':
    print("main entered")

    try:
        app.run(debug=True, port=80)
        print("app.run(port=80)")
    except:
        print("app.shutdown")
        app.shutdown()
