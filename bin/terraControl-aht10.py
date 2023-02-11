#!/usr/bin/env python3

import smbus
import time
from gpiozero import LED
import syslog, os

## AHT10 CONFIG

bus = smbus.SMBus(1)

cmdInit = [0x08, 0x00]
cmdMeasure = [0x33, 0x00]

i2cAddr = 0x38
offsetInit = 0xE1
offsetMeasure = 0xAC
i2cSleep = 0.2

## HEATER AND LIGHT CONFIG

heater = LED(18)
light = LED(24)

### VARIABLES ###

heatingTime = 5
heatingTimeout = 5
heatingCycle = 6
overheatTimeout = 60

dayTemp = 27
nightTemp = 24
maxTemp = dayTemp

dayStart = "08:00"
nightStart  = "18:00"

logFileTemp = "/mnt/terraControl/tempAll.csv"
logFileTempLast10 = "/mnt/terraControl/tempLast10.csv"
logFileTempLast24h = "/mnt/terraControl/tempLast24h.csv"
logFileHum = "/mnt/terraControl/humAll.csv"
logFileHumLast10 = "/mnt/terraControl/humLast10.csv"
logFileHumLast24h = "/mnt/terraControl/humLast24h.csv"
logIdent = "terraControl"


###


def heatingON():

  syslog.syslog(syslog.LOG_INFO, "Turning heating cycle ON")
  
  for x in range(0,heatingCycle):

    heater.on()
    sleep(heatingTime)
    heater.off()

  syslog.syslog(syslog.LOG_INFO, "Turning heating cycle OFF")
  sleep(heatingTimeout)

syslog.openlog(logIdent)

## INIT SENSOR
bus.write_i2c_block_data(i2cAddr, offsetInit, cmdInit)
time.sleep(i2cSleep)

while True:

  currentTime = strftime("%H:%M", localtime())
  currentDate = strftime("%Y-%m-%d", localtime())

  bus.write_i2c_block_data(i2cAddr, offsetMeasure, cmdMeasure)
  time.sleep(i2cSleep)

  data = bus.read_i2c_block_data(i2cAddr,0x00)

  temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
  convTemp = ((temp*200) / 1048576) - 50

  hum = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
  convHum = int(hum * 100 / 1048576)

  humidity = f"{convHum}"
  temperature = f"{convTemp:.1f}"

  f = open(logFileTemp, "a")
  f.writelines(currentDate + ' ' + currentTime + ',' + str(temperature) + '\n')
  f.close()

  f = open(logFileHum, "a")
  f.writelines(currentDate + ' ' + currentTime + ',' + str(humidity) + '\n')
  f.close()

  os.system('tail -n10 %s >%s' %(logFileTemp,logFileTempLast10))

  os.system('tail -n1180 %s > %s' %(logFileTemp,logFileTempLast24h))

  os.system('tail -n10 %s >%s' %(logFileHum,logFileHumLast10))

  os.system('tail -n1180 %s > %s' %(logFileHum,logFileHumLast24h))

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

