#!/bin/python3

import os, syslog
from gpiozero import LED
from time import localtime, strftime, sleep

### VARIABLES ###

light = LED(24)
interval_day = 600
interval_night = 600
dayStart = "08:00"
nightStart  = "18:00"

picQuality = 95
picBrightness = 50
picRotation = 270
picRoi = "0,0.1,0.8,0.8"
picWidth = 500
picHight = 500
picOutput = "/mnt/terraControl/view.jpg"

###

while True:

  currentTime = strftime("%H:%M", localtime())

  if (currentTime >= dayStart) and (currentTime < nightStart):

    syslog.syslog(syslog.LOG_INFO, "Turning light ON")
    light.on()
    syslog.syslog(syslog.LOG_INFO, "Taking picture")
    os.system('raspistill -q %s -br %s -rot %s -roi %s -w %s -h %s -n -o %s' %(picQuality, picBrightness, picRotation, picRoi, picWidth, picHight, picOutput))
    syslog.syslog(syslog.LOG_INFO, "Turning light OFF")
    light.off()
    sleep(interval_day)

  else:

      sleep(interval_night)

