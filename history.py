import time
import os
import gc


class History:
    def __init__(self):
        NotImplemented

    def fileExists(self, filename):
        try:
            os.stat(filename)
            return True
        except OSError:
            return False

    def getLogData(self, begin, end=int(time.time())):
        gc.collect()
        # Will get all the data between two times
        # if more than 7 days between dates then summarize to daily totals.
        entries = {}
        sm1Total = 0
        sm2Total = 0
        batTotal = 0
        tempTotal = 0
        humidityTotal = 0
        waterLevelTotal = 0
        pumpTotal = 0
        camTotal = 0
        hoursTotal = 0
        # After 6 days of 24 hours data output I was getting memory allocation (JSON size?)
        # errors, so started summarizing after 4 days data. Maybe will need to summarize by week after 90 days?
        #         Traceback (most recent call last):
        #            File "/lib/microdot_asyncio.py", line 378, in dispatch_request
        #            File "/lib/microdot.py", line 540, in __init__
        #         MemoryError: memory allocation failed, allocating 11288 bytes
        SUMMARIZE_DAYS = 4

        summarize = True if ((end-begin)/(60*60*24)
                             ) > SUMMARIZE_DAYS else False
        # if summarize:
        #     print("Summarize:", ((end-begin)/(60*60*24)))
        startOfBeginDay = begin - \
            (time.localtime(begin)[3] * 60 * 60) - \
            (time.localtime(begin)[4] * 60) + 1
        for fileDate in range(startOfBeginDay, end, (60*60*24)):
            logMonth = str(time.localtime(fileDate)[1])
            if len(logMonth) == 1:
                logMonth = "0" + logMonth
            logDay = str(time.localtime(fileDate)[2])
            if len(logDay) == 1:
                logDay = "0" + logDay
            logName = "/log/" + \
                str(time.localtime(fileDate)[0]) + logMonth + logDay + ".csv"
            # print("getHistory logName:", logName, fileDate)
            if self.fileExists(logName):
                with open(logName, "r") as loggingFile:
                    # filter out entries that are not in required range
                    loggingFileLines = loggingFile.readlines()
                    for line in loggingFileLines:
                        lineValues = line.split(",")
                        if int(lineValues[0]) >= begin and int(lineValues[0]) <= end:
                            if summarize:
                                # Summarize a days data
                                sm1Total += int(lineValues[1])
                                sm2Total += int(lineValues[2])
                                batTotal += float(lineValues[3])
                                tempTotal += float(lineValues[4])
                                humidityTotal += float(lineValues[5])
                                pumpTotal += int(lineValues[6])
                                camTotal += int(lineValues[7])
                                waterLevelTotal += int(lineValues[8])
                                hoursTotal += 1
                            else:
                                # Build dictionary item for current hour
                                entries[int(lineValues[0])] = {"timeStamp": int(lineValues[0]), "sm1": int(lineValues[1]), "sm2": int(lineValues[2]), "bat": float(lineValues[3]), "temp": float(
                                    lineValues[4]), "humidity": float(lineValues[5]), "pump": int(lineValues[6]), "cam": int(lineValues[7]), "waterLevel": int(lineValues[8])}
                    if summarize:
                        startOfDay = fileDate - \
                            (time.localtime(fileDate)[3] * 60 * 60) - \
                            (time.localtime(fileDate)[4] * 60) + 1
                        if hoursTotal > 0:
                            entries[startOfDay] = {"timeStamp":  startOfDay, "sm1": sm1Total/hoursTotal, "sm2": sm2Total/hoursTotal, "bat": batTotal/hoursTotal, "temp": tempTotal /
                                                   hoursTotal, "humidity": humidityTotal/hoursTotal, "pump": pumpTotal, "cam": camTotal, "waterLevel": waterLevelTotal/hoursTotal}
                        sm1Total = 0
                        sm2Total = 0
                        batTotal = 0
                        tempTotal = 0
                        humidityTotal = 0
                        waterLevelTotal = 0
                        pumpTotal = 0
                        camTotal = 0
                        hoursTotal = 0
        # print("entries:", entries)
        return entries
