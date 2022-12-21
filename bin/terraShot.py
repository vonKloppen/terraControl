#!/bin/python3

import os, syslog
from gpiozero import LED
from time import sleep

### VARIABLES ###

light = LED(24)
interval = 180

###

while True:

  sleep(interval)
  syslog.syslog(syslog.LOG_INFO, "Turning light ON")
  light.on()
  syslog.syslog(syslog.LOG_INFO, "Taking picture")
  os.system('raspistill -q 100 -br 50 -rot 270 -roi 0,0.1,0.8,0.8 -w 500 -h 500 -n -o /mnt/terraControl/view.jpg')
  syslog.syslog(syslog.LOG_INFO, "Turning light OFF")
  light.off()
