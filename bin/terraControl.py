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
logFileLast24h = "/mnt/terraControl/last24h.csv"
dayTemp = 27
nightTemp = 24
maxTemp = dayTemp
dayStart = "08:00"
nightStart  = "18:00"

###

def heatingON():

  syslog.syslog(syslog.LOG_INFO, "Turning heater ON")
  heater.on()
  sleep(heatingTime)

  syslog.syslog(syslog.LOG_INFO, "Turning heater OFF")
  heater.off()
  sleep(heatingTimeout)


while True:

  currentTime = strftime("%H:%M", localtime())
  currentDate = strftime("%Y-%m-%d", localtime())
  temperature = sensor.get_temperature()

  f = open(logFile, "a")
  f.writelines(currentDate + ' ' + currentTime + ',' + str(temperature) + '\n')
  f.close()

  os.system('tail -n10 %s >%s' %(logFile,logFileLast10))

  os.system('tail -n1100 %s > %s' %(logFile,logFileLast24h))

  if (currentTime >= dayStart) and (currentTime < nightStart):

    maxTemp = dayTemp

  else:

    maxTemp = nightTemp


  if temperature < maxTemp:

    heatingON()

  else:

    heater.off()
    sleep(overheatTimeout)

