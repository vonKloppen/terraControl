#!/bin/python3

from time import localtime,  strftime, sleep
from gpiozero import LED
import w1thermsensor

heater = LED(18)
sensor = w1thermsensor.W1ThermSensor()

### VARIABLES ###

heatingTime = 60
heatingTimeout = 20
overheatTimeout = 60
logFile = "/mnt/terraControl/temperature.csv"
maxTemp = 26

###

def heatingON():

  heater.on()
  sleep(heatingTime)

  heater.off()
  sleep(heatingTimeout)


while True:

  currentTime = strftime("%Y-%m-%d %H:%M", localtime())
  temperature = sensor.get_temperature()

  f = open(logFile, "a")
  f.writelines(currentTime + ',' + str(temperature) + '\n')
  f.close()

  if temperature < maxTemp:

    heatingON()

  else:

    heater.off()
    sleep(overheatTimeout)

