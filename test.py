from iotwifi import IOTwifi
import os

def getFreespaceKB():
    stat = os.statvfs("/")
    free = stat[0] * stat[3]
    return free / 1024

print(getFreespaceKB())

if getFreespaceKB() < 100:
    #  Remove oldest log
    oldestLog = "zzzzzzzzzzzzzzz"
    for filename in os.listdir("/log"):
        print(filename,oldestLog)
        if filename < oldestLog:
            oldestLog = filename
    os.remove("/log/" + oldestLog)

# iotwifi = IOTwifi(False)
# if iotwifi.connect():
#     iotwifi.sendClimate(30,47)
#     iotwifi.sendGarden(40,60,3,30,4,12.6)
