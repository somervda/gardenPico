import time


def toEasternStandardTime(gmTime):
    # Adjust current time to eastern time zone
    esTime = gmTime
    # Check if it is daylight saving time
    if time.localtime()[1] >= 3 and time.localtime()[2] >= 12 and time.localtime()[1] <= 11 and time.localtime()[2] >= 5:
        esTime -= 3600*4
    else:
        esTime -= 3600*5
    return esTime
