# **What is it precious?**

It's a simple "daemon" for monitoring temperature in terrarium, using ds18b20 sensor and Raspberry PI Zero.
It creates log as csv file. Also it can control light.

www folder contains stupidly simple html page with graphs using AnyChart scripts (https://www.anychart.com/)

***Be aware that this is highly customized sollution and a work in progress and you should probably not use this code for controling temperature in terrarium with live animals!***


## **TO-DO**

 - [ ] Move variables to config file - writing parser needed
 - [ ] Add simple www server (python) for displaying chart directly on Raspberry
 - [ ] Add configuration change from www ( [ ] Add default absolute max temperature and time of heating, [ ] Password protection )
 - [ ] Add option to choose time and date for chart
 - [x] Convert epoch to human-readeable dates/times
 - [x] Add watchdog service
 - [x] Add catch photo with lighting
