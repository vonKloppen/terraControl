#!/usr/bin/env python3

from time import localtime, strftime, sleep
from gpiozero import LED
import w1thermsensor, syslog, os

heater = LED(18)
light = LED(24)
sensor = w1thermsensor.W1ThermSensor()

### VARIABLES ###

heatingTime = 60
heatingTimeout = 10
overheatTimeout = 60

dayTemp = 27
nightTemp = 24
maxTemp = dayTemp

dayStart = "08:00"
nightStart  = "18:00"

logFile = "/mnt/terraControl/all.csv"
logFileLast10 = "/mnt/terraControl/last10.csv"
logFileLast24h = "/mnt/terraControl/last24h.csv"
logIdent = "terraControl"


###

def heatingON():

  syslog.syslog(syslog.LOG_INFO, "Turning heater ON")
  heater.on()
  sleep(heatingTime)

  heater.off()
  syslog.syslog(syslog.LOG_INFO, "Turning heater OFF")
  sleep(heatingTimeout)

syslog.openlog(logIdent)

while True:

  currentTime = strftime("%H:%M", localtime())
  currentDate = strftime("%Y-%m-%d", localtime())
  
  try:
    
    temperature = sensor.get_temperature()

  except:

    syslog.syslog(syslog.LOG_INFO, "Error communicating with sensor. Turning heater off.")
    heater.off()

  f = open(logFile, "a")
  f.writelines(currentDate + ' ' + currentTime + ',' + str(temperature) + '\n')
  f.close()

  os.system('tail -n10 %s >%s' %(logFile,logFileLast10))

  os.system('tail -n1180 %s > %s' %(logFile,logFileLast24h))

  if (currentTime >= dayStart) and (currentTime < nightStart):

    if (maxTemp == nightTemp):

      syslog.syslog(syslog.LOG_INFO, "Daytime, turning lights ON")

    light.on()
    maxTemp = dayTemp

  else:

    if (maxTemp == dayTemp):

      syslog.syslog(syslog.LOG_INFO, "Nighttime - turning lights OFF")

    light.off()
    maxTemp = nightTemp

  if temperature < maxTemp:

    heatingON()

  else:

    syslog.syslog(syslog.LOG_INFO, "MAX temperature reached. Sleeping..")
    heater.off()
    sleep(overheatTimeout)

syslog.closelog()
heater.off()

