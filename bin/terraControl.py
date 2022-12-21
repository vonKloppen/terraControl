#!/bin/python3

from time import localtime,  strftime, sleep
from gpiozero import LED
import w1thermsensor, syslog

heater = LED(18)
sensor = w1thermsensor.W1ThermSensor()

### VARIABLES ###

heatingTime = 60
heatingTimeout = 10
overheatTimeout = 60
logFile = "/mnt/terraControl/all.csv"
logFileLast10 = "/mnt/terraControl/last10.csv"
maxTemp = 26

###

def heatingON():

  syslog.syslog(syslog.LOG_INFO, "Turning heater ON")
  heater.on()
  sleep(heatingTime)

  syslog.syslog(syslog.LOG_INFO, "Turning heater OFF")
  heater.off()
  sleep(heatingTimeout)


while True:

  currentTime = strftime("%Y-%m-%d %H:%M", localtime())
  temperature = sensor.get_temperature()

  f = open(logFile, "a")
  f.writelines(currentTime + ',' + str(temperature) + '\n')
  f.close()

## Whipe stripted log file.

  f_strip = open(logFileLast10, "w")
  f_strip.close()

##

  f_full = open(logFile, "r")
 
  for line in (f_full.readlines() [-10:]):

    f_strip = open(logFileLast10, "a")
    f_strip.writelines(line)
    f_strip.close()

  f_full.close()

  if temperature < maxTemp:

    heatingON()

  else:

    heater.off()
    sleep(overheatTimeout)

