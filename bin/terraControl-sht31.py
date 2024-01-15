#!/usr/bin/env python3

import smbus
from time import localtime, strftime, sleep
from gpiozero import LED
from oled import OLED, Font, Graphics
import syslog, os, sys, signal

### SHT31 CONFIG ###

## raspi-config - enable i2c
## otherwise error will occur "no such file or directory"

bus = smbus.SMBus(1)

i2cAddr = 0x44
i2cSleep = 0.5


### OLED CONFIG ###

dispOn = False

if dispOn:

    disp = OLED(1)
    disp.begin()
    disp.initialize()

    disp.set_memory_addressing_mode(0)
    disp.set_column_address(0, 127)
    disp.set_page_address(0, 7)

    disp.deactivate_scroll()
    disp.clear()


### HEATER AND LIGHT CONFIG ###

heater = LED(15)
light = LED(14)
fan = LED(18)

###

### VARIABLES ###

heatingTime = 60
heatingTimeout = 5
overheatTimeout = 60

dayTemp = 28
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
  fan.off()
  syslog.syslog(syslog.LOG_INFO, "Turning lights OFF")
  light.off()

  if dispOn:
      
      updateDisplay("off")

  sys.exit()


if __name__ == '__main__':

  signal.signal(signal.SIGHUP, signal.SIG_IGN)
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  signal.signal(signal.SIGQUIT, terminate)
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

def updateDisplay(status):

    if status == "off":

        disp.clear()
        dispFont = Font(4)
        dispFont.print_string(0, 0, "Off")
        disp.update()
        disp.close()
        return None


    disp.clear()
    dispFont = Font(3)
    dispFont.print_string(0, 0, "T: " + tempTrimmed)
    dispFont.print_string(0, 27, "H: " + humTrimmed)

    if status == "h_on":

        dispFont = Font(1)
        Graphics.draw_circle(4,56,3)

    disp.update()


def heatingON():

  syslog.syslog(syslog.LOG_INFO, "Turning heating cycle ON")
  
  heater.on()
  fan.on()

  if dispOn:

      updateDisplay("h_on")

  sleep(heatingTime)
  heater.off()
  fan.off()
  
  if dispOn:

      updateDisplay("none")

  syslog.syslog(syslog.LOG_INFO, "Turning heating cycle OFF")
  sleep(heatingTimeout)

syslog.openlog(logIdent)


while True:

  currentTime = strftime("%H:%M", localtime())
  currentDate = strftime("%Y-%m-%d", localtime())

  try:

    bus.write_i2c_block_data(i2cAddr, 0x2C, [0x06])
    sleep(i2cSleep)

  except:

    msg = f"Error (E1) communicating with sensor. Turning heater off."
    syslog.syslog(syslog.LOG_INFO, msg)
    heater.off()
    fan.off()
    sys.exit()

  try:

    data = bus.read_i2c_block_data(i2cAddr, 0x00, 6)

  except:

    msg = f"Error (E2) communicating with sensor. Turning heater off."
    syslog.syslog(syslog.LOG_INFO, msg)
    heater.off()
    fan.off()
    sys.exit()

  else:

    temperature = data[0] * 256 + data[1]
    tempConv = -45 + (175 * temperature / 65535.0)
    humConv = 100 * (data[3] * 256 + data[4]) / 65535.0
    tempTrimmed = f"{tempConv:.1f}"
    humTrimmed = f"{humConv:.1f}"

    if dispOn:

        updateDisplay("none")

  try:

    f = open(logFileTemp, "a")

  except:

    msg = f"Error opening logfile {logFileTemp}"
    syslog.syslog(syslog.LOG_INFO, msg)

  else:

    f.writelines(currentDate + ' ' + currentTime + ',' + str(tempTrimmed) + '\n')
    f.close()
    os.system('tail -n10 %s >%s' %(logFileTemp,logFileTempLast10))
    os.system('tail -n1180 %s > %s' %(logFileTemp,logFileTempLast24h))

  try:

    f = open(logFileHum, "a")

  except:

    msg = f"Error opening logfile {logFileHum}"
    syslog.syslog(syslog.LOG_INFO, msg)

  else:

    f.writelines(currentDate + ' ' + currentTime + ',' + str(humTrimmed) + '\n')
    f.close()
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

  if float(tempConv) < maxTemp:

    heatingON()

  else:

    syslog.syslog(syslog.LOG_INFO, "MAX temperature reached. Sleeping..")
    heater.off()
    fan.off()
    sleep(overheatTimeout)

syslog.closelog()
heater.off()
fan.off()

