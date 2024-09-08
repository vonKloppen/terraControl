#!/usr/bin/env python3

import smbus2
import time

### AHT10 CONFIG ###

## raspi-config - enable i2c
## otherwise error will occur "no such file or directory"

bus = smbus2.SMBus(1)

cmdInit = [0x08, 0x00]
cmdMeasure = [0x33, 0x00]

i2cAddr = 0x38
offsetInit = 0xE1
offsetMeasure = 0xAC
i2cSleep = 0.2

bus.write_i2c_block_data(i2cAddr, offsetInit, cmdInit)
time.sleep(i2cSleep)

bus.write_i2c_block_data(i2cAddr, offsetMeasure, cmdMeasure)
time.sleep(i2cSleep)

data = bus.read_i2c_block_data(i2cAddr,0x00)

temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
convTemp = ((temp*200) / 1048576) - 50

hum = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
convHum = int(hum * 100 / 1048576)

print(f"Temperature: {convTemp:.1f}°C")
print(f"Humidity: {convHum}%")
