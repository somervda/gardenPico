import machine
pumpRelay = machine.Pin(15, machine.Pin.OUT)
pumpRelay.value(0)
pumpValue = "off"


def pumpOn():
    global pumpValue
    pumpRelay.on()
    pumpValue = "on"


def pumpOff():
    global pumpValue
    pumpRelay.off()
    pumpValue = "off"


def getPump():
    global pumpValue
    return pumpValue
