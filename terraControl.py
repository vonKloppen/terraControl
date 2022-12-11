#!/bin/python3

import time
from time import sleep
from gpiozero import LED
import w1thermsensor

grzalka = LED(18)
czujnik = w1thermsensor.W1ThermSensor()

### VARIABLES ###

heatingTime = 60
heatingTimeout = 20
overheatTimeout = 60
logFile = "/var/log/terraControl.log"
maxTemp = 26

###

def heatingON():

  grzalka.on()
  sleep(heatingTime)

  grzalka.off()
  sleep(heatingTimeout)


while True:

  currentTime = int(time.time())
  temperatura = czujnik.get_temperature()

  f = open(logFile, "a")
  f.writelines(str(currentTime) + ',' + str(temperatura) + '\n')
  f.close()

  if temperatura < maxTemp:

    heatingON()

  else:

    grzalka.off()
    sleep(overheatTimeout)

