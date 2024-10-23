#!/usr/bin/env python3

import os, syslog
from gpiozero import LED
from time import localtime, strftime, sleep

### VARIABLES ###

interval_day = 600
interval_night = 600
dayStart = "08:00"
nightStart  = "18:00"

picOutputTemp = "/mnt/terraControl/view.temp"
picOutputTemp1 = "/mnt/terraControl/view.temp1"
picOutput = "/mnt/terraControl/view.jpg"

###

while True:

  currentTime = strftime("%H:%M", localtime())

  if (currentTime >= dayStart) and (currentTime < nightStart):

    syslog.syslog(syslog.LOG_INFO, "Taking picture")
    os.system('rpicam-still --awb tungsten --immediate 1 --brightness 0.15 -o %s' %(picOutputTemp))
    os.system('convert %s -crop 2140x2464+680+0 %s' %(picOutputTemp, picOutputTemp1))
    os.system('convert %s -rotate 90 %s' %(picOutputTemp1, picOutput))
    sleep(interval_day)

  else:

      sleep(interval_night)

