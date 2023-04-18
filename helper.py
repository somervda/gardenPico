import time


def setLocalTimeOffset(self):
    # Set a UMT offset value (For eastern time me)
    monthDay = time.localtime()[1] * 100 + time.localtime()[2]
    if monthDay >= 312 and monthDay <= 1105:
        self._loadSettings()
        self._settings["umt_offset"] = -4 * 60 * 60
        self._saveSettings()
    else:
        self._loadSettings()
        self._settings["umt_offset"] = -5 * 60 * 60
        self._saveSettings()


def getLocalTime(self):
    self._loadSettings()
    return time.time() + self._settings["umt_offset"]
