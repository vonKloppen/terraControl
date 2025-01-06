#!/usr/bin/env python3

import smbus2, syslog, os, sys, signal, socket
from time import localtime, strftime, sleep
from gpiozero import LED


### SHT31 CONFIG ###

## raspi-config - enable i2c
## otherwise error will occur "no such file or directory"

bus = smbus2.SMBus(1)

i2cAddr = 0x44
i2cSleep = 0.5

### HEATER AND LIGHT CONFIG ###

heater = LED(17)
light = LED(4)
fan = LED(18)

###

### Display config ###

displayEnabled = True
socketFile = "/run/terraDisplay.socket"

###

### Log config ###

logFileTemp = "/mnt/terraControl/tempAll.csv"
logFileTempLast10 = "/mnt/terraControl/tempLast10.csv"
logFileTempLast24h = "/mnt/terraControl/tempLast24h.csv"
logFileHum = "/mnt/terraControl/humAll.csv"
logFileHumLast10 = "/mnt/terraControl/humLast10.csv"
logFileHumLast24h = "/mnt/terraControl/humLast24h.csv"
logIdent = "terraControl"

logPath = "/mnt/terraControl"

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

###


## SIGNAL HANDLING ###

def terminate(signalNumber, frame):

    updateDisplay("X","1","0","0")
    syslog.syslog(syslog.LOG_INFO, "SIGTERM received. Terminating..")
    syslog.syslog(syslog.LOG_INFO, "Turning heater OFF")
    heater.off()
    fan.off()
    syslog.syslog(syslog.LOG_INFO, "Turning lights OFF")
    light.off()
    syslog.closelog()
    sys.exit(0)


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

def heatingON():

    updateDisplay("H", "1", tempTrimmed, humTrimmed)
    syslog.syslog(syslog.LOG_INFO, "Turning heating cycle ON")
    heater.on()
    fan.on()
    sleep(heatingTime)
    heater.off()
    fan.off()
    updateDisplay("S", "1", tempTrimmed, humTrimmed)
    syslog.syslog(syslog.LOG_INFO, "Turning heating cycle OFF")
    sleep(heatingTimeout)

def updateDisplay(status,ident,temp,hum):

    if displayEnabled:

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            client.connect(socketFile)

        except:
            syslog.syslog(syslog.LOG_ERR, "Can't bind to display socket.")
            client.close()

        else:
            message = str(status + "," + ident + "," + temp + "," + hum)
            client.send(message.encode("utf-8")[:1024])
            client.close()


syslog.openlog(logIdent)



while True:

    currentTime = strftime("%H:%M", localtime())
    currentDate = strftime("%Y-%m-%d", localtime())

    try:

      bus.write_i2c_block_data(i2cAddr, 0x2C, [0x06])
      sleep(i2cSleep)

    except:

      updateDisplay("E1", "1", "0", "0")
      msg = f"Error (E1) communicating with sensor. Turning heater off."
      syslog.syslog(syslog.LOG_ERR, msg)
      heater.off()
      fan.off()
      syslog.closelog()
      sys.exit(1)

    try:

      data = bus.read_i2c_block_data(i2cAddr, 0x00, 6)

    except:

      updateDisplay("E2", "1", "0", "0")
      msg = f"Error (E2) communicating with sensor. Turning heater off."
      syslog.syslog(syslog.LOG_ERR, msg)
      heater.off()
      fan.off()
      syslog.closelog()
      sys.exit(1)

    else:

      temperature = data[0] * 256 + data[1]
      tempConv = -45 + (175 * temperature / 65535.0)
      humConv = 100 * (data[3] * 256 + data[4]) / 65535.0
      tempTrimmed = f"{tempConv:.1f}"
      humTrimmed = f"{humConv:.1f}"
      updateDisplay("R", "1", tempTrimmed, humTrimmed)
      msg = f"Reading temperature."
      syslog.syslog(syslog.LOG_INFO, msg)

    try:

      f = open(logFileTemp, "a")

    except:

      msg = f"Error opening logfile {logFileTemp}"
      syslog.syslog(syslog.LOG_ERR, msg)

    else:

      f.writelines(currentDate + ' ' + currentTime + ',' + str(tempTrimmed) + '\n')
      f.close()
      os.system('tail -n10 %s >%s' %(logFileTemp,logFileTempLast10))
      os.system('tail -n1180 %s > %s' %(logFileTemp,logFileTempLast24h))

    try:

      f = open(logFileHum, "a")

    except:

      msg = f"Error opening logfile {logFileHum}"
      syslog.syslog(syslog.LOG_ERR, msg)

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

      updateDisplay("S", "1", tempTrimmed, humTrimmed)
      syslog.syslog(syslog.LOG_INFO, "MAX temperature reached. Sleeping..")
      heater.off()
      fan.off()
      sleep(overheatTimeout)


syslog.closelog()
heater.off()
fan.off()
syslog.closelog()
