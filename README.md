# **What is it precious?**

It's a simple "daemon" for monitoring temperature and humidity in terrarium, using different sensors and Raspberry PI Zero.
It creates log as csv file and logs to syslog. Also it can control light and camera.

www folder contains stupidly simple html page with graphs using AnyChart scripts (https://www.anychart.com/)

***Be aware that this is highly customized sollution and a work in progress and you should probably not use this code for controling temperature in terrarium with live animals!***

## **Prerequisites**

*raspi-config - enable i2c*

*pip3 install smbus mod-oled-128x64*

*reboot*

## **TO-DO**

### Functionality

 - [ ] Move variables to config file - config file parser needed
 - [ ] Add simple www server (python) for displaying chart directly on Raspberry
 - [ ] ~~Add configuration change from www ( [ ] Add default absolute max temperature and time of heating, [ ] Password protection )~~
 - [ ] Add option to choose time and date for chart
 - [ ] Add API with status in JSON
 - [x] Convert epoch to human-readeable dates/times
 - [x] Add watchdog service
 - [x] Add catch photo with lighting
 - [x] Logging to syslog
 - [x] Signal handling (systemd)
 - [x] OLED display

### Modules

**UPS:**

*As separate daemon: https://github.com/vonKloppen/raspiUPS

- [x] Monitoring service
- [x] Clean shutdown of PI
- [x] Logging to syslog

**OLED display:**

- [ ] Reads values from API (terraControl, ?terraUPS?)
- [ ] Sets values ?temporary/permanent (writes to file)? by ?signal/socket? 
- [ ] Menu (light ON/OFF, Heater ON/OFF, Poweroff, Reboot, Set HH:MM day/night, Timeouts)
- [ ] Logging to syslog






