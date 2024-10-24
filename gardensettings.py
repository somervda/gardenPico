
import json


class GardenSettings:
    # Persist settings in a gardenSettings.json file
    def __init__(self):
        self._loadSettings()

    def _loadSettings(self):
        try:
            with open("gardenSettings.json", "r") as gardenSettingsFile:
                self._settings = json.load(gardenSettingsFile)
        except:
            self._settings = {}

    def _saveSettings(self):
        with open("gardenSettings.json", "w") as gardenSettingsFile:
            json.dump(self._settings, gardenSettingsFile)

    # How long the pump should run when turned on
    def getPumpOnSeconds(self):
        self._loadSettings()
        if "pumpOnSeconds" in self._settings:
            return self._settings["pumpOnSeconds"]
        else:
            return None

    def setPumpOnSeconds(self, seconds):
        self._loadSettings()
        self._settings["pumpOnSeconds"] = seconds
        self._saveSettings()
        return seconds

    # How long the camera should run when turned on
    def getCamOnMinutes(self):
        self._loadSettings()
        if "camOnMinutes" in self._settings:
            return self._settings["camOnMinutes"]
        else:
            return None

    def setCamOnMinutes(self, minutes):
        self._loadSettings()
        self._settings["camOnMinutes"] = minutes
        self._saveSettings()
        return minutes

    # Moisture sensor reading for when the pump should do an auto water
    # I.e. turn on pump if moisture level is below 3
    def getPumpMSTriggerOn(self):
        self._loadSettings()
        if "pumpMSTriggerOn" in self._settings:
            return self._settings["pumpMSTriggerOn"]
        else:
            return None

    def setPumpMSTriggerOn(self, msLevel):
        self._loadSettings()
        self._settings["pumpMSTriggerOn"] = msLevel
        self._saveSettings()
        return msLevel

    # Moisture sensor reading for when the pump should not turn on the pump
    # I.e. never turn on the pump if moisture level over 8
    def getPumpMSBlock(self):
        self._loadSettings()
        if "pumpMSBlock" in self._settings:
            return self._settings["pumpMSBlock"]
        else:
            return None

    def setPumpMSBlock(self, msLevel):
        self._loadSettings()
        self._settings["pumpMSBlock"] = msLevel
        self._saveSettings()
        return msLevel

    # comma delimited list of times (24 hour times) to turn on the pump
    #  i.e. 630,1400,2200
    def getPumpTimes(self):
        self._loadSettings()
        if "pumpTimes" in self._settings:
            return self._settings["pumpTimes"]
        else:
            return None

    def setPumpTimes(self, times):
        self._loadSettings()
        self._settings["pumpTimes"] = times
        self._saveSettings()
        return times
    
    # WiFI settings
    def getHostname(self):
        self._loadSettings()
        if "hostname" in self._settings:
            return self._settings["hostname"]
        else:
            return None
        
    def getSSID(self):
        self._loadSettings()
        if "ssid" in self._settings:
            return self._settings["ssid"]
        else:
            return None
        
    def getPassword(self):
        self._loadSettings()
        if "password" in self._settings:
            return self._settings["password"]
        else:
            return None
        
    # IOT system settings

    def getIotHost(self):
        self._loadSettings()
        if "iotHost" in self._settings:
            return self._settings["iotHost"]
        else:
            return None
        
    def getIotPort(self):
        self._loadSettings()
        if "iotPort" in self._settings:
            return self._settings["iotPort"]
        else:
            return None
        
    def getIotUser(self):
        self._loadSettings()
        if "iotUser" in self._settings:
            return self._settings["iotUser"]
        else:
            return None
        
    def getCLIMATE_ID(self):
        self._loadSettings()
        if "CLIMATE_ID" in self._settings:
            return self._settings["CLIMATE_ID"]
        else:
            return None
        
    def getDEVICE_ID(self):
        self._loadSettings()
        if "DEVICE_ID" in self._settings:
            return self._settings["DEVICE_ID"]
        else:
            return None