#!/bin/python3

import os, syslog
from gpiozero import LED
from time import sleep

### VARIABLES ###

light = LED(24)
interval = 180

picQuality = 95
picBrightness = 50
picRotation = 270
picRoi = "0,0.1,0.8,0.8"
picWidth = 500
picHight = 500
picOutput = "/mnt/terraControl/view.jpg"

###

while True:

  sleep(interval)
  syslog.syslog(syslog.LOG_INFO, "Turning light ON")
  light.on()
  syslog.syslog(syslog.LOG_INFO, "Taking picture")
  os.system('raspistill -q %s -br %s -rot %s -roi %s -w %s -h %s -n -o %s' %(picQuality, picBrightness, picRotation, picRoi, picWidth, picHight, picOutput))
  syslog.syslog(syslog.LOG_INFO, "Turning light OFF")
  light.off()

