import os
import time
import io
import sys


LOGFILE = "logger.txt"


class Logger:
    def __init__(self):
        NotImplemented

    def fileExists(self):
        try:
            os.stat(LOGFILE)
            return True
        except OSError:
            return False

    def getTimeStamp(self):
        formatedTime = ""
        now = time.localtime()
        formatedTime = "{}-{}-{} {}:{}:{}".format(
            now[0], now[1], now[2], now[3], now[4], now[5])
        return formatedTime

    def writeLogLine(self, logLine):
        with open(LOGFILE, "a") as logFile:
            logFile.write(self.getTimeStamp() + " " +
                          logLine.replace("\n", "\t") + "\n")

    def writeException(self, e):
        s = io.StringIO()
        sys.print_exception(e, s)
        self.writeLogLine(s.getvalue())

    def getLog(self):
        with open(LOGFILE, "r") as logFile:
            return logFile.read().replace("\n", "<br>")

    def clearLog(self):
        with open(LOGFILE, "w") as logFile:
            logFile.write("")
