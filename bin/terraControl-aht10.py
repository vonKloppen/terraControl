#!/usr/bin/env python3

import smbus
from time import localtime, strftime, sleep
from gpiozero import LED
import syslog, os, sys, signal

### AHT10 CONFIG ###

bus = smbus.SMBus(1)

cmdInit = [0x08, 0x00]
cmdMeasure = [0x33, 0x00]

i2cAddr = 0x38
offsetInit = 0xE1
offsetMeasure = 0xAC
i2cSleep = 0.2

###

### HEATER AND LIGHT CONFIG ###

heater = LED(18)
light = LED(24)

###

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

## SIGNAL HANDLING ###

def terminate(signalNumber, frame):

  syslog.syslog(syslog.LOG_INFO, "SIGTERM received. Terminating..")
  syslog.syslog(syslog.LOG_INFO, "Turning heater OFF")
  heater.off()
  syslog.syslog(syslog.LOG_INFO, "Turning lights OFF")
  light.off()
  sys.exit()


if __name__ == '__main__':

  signal.signal(signal.SIGHUP, signal.SIG_IGN)
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  signal.signal(signal.SIGQUIT, signal.SIG_IGN)
  signal.signal(signal.SIGILL, signal.SIG_IGN)
  signal.signal(signal.SIGTRAP, signal.SIG_IGN)
  signal.signal(signal.SIGABRT, signal.SIG_IGN)
  signal.signal(signal.SIGBUS, signal.SIG_IGN)
  signal.signal(signal.SIGFPE, signal.SIG_IGN)
  signal.signal(signal.SIGUSR1, signal.SIG_IGN)
  signal.signal(signal.SIGSEGV, signal.SIG_IGN)
  signal.signal(signal.SIGUSR2, signal.SIG_IGN)
  signal.signal(signal.SIGPIPE, signal.SIG_IGN)
  signal.signal(signal.SIGALRM, signal.SIG_IGN)
  signal.signal(signal.SIGTERM, terminate)

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
sleep(i2cSleep)

###


while True:

  currentTime = strftime("%H:%M", localtime())
  currentDate = strftime("%Y-%m-%d", localtime())

  bus.write_i2c_block_data(i2cAddr, offsetMeasure, cmdMeasure)
  sleep(i2cSleep)

  data = bus.read_i2c_block_data(i2cAddr,0x00)

  temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
  convTemp = ((temp*200) / 1048576) - 50

  hum = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
  convHum = int(hum * 100 / 1048576)

  humidity = f"{convHum}"
  temperature = f"{convTemp:.1f}"

  try:
    
    f = open(logFileTemp, "a")
    
  except:
    
    msg = f"Error opening logfile {logFileTemp}. Quitting.."
    syslog.syslog(syslog.LOG_INFO, msg)
    sys.exit()

  else:
    
    f.writelines(currentDate + ' ' + currentTime + ',' + str(temperature) + '\n')
    f.close()

  try:

    f = open(logFileHum, "a")

  except:

    msg = f"Error opening logfile {logFileHum}. Quitting.."
    syslog.syslog(syslog.LOG_INFO, msg)
    sys.exit()

  else:

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

