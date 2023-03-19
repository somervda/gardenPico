import relay
from microdot_asyncio import Microdot,  send_file, Response

app = Microdot()


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
    try:
        app.run(debug=True, port=80)
        print("app.run(port=80)")
    except:
        print("app.shutdown")
        app.shutdown()
