#!/usr/bin/env python3

import smbus2
import time

### SHT31 CONFIG ###

## raspi-config - enable i2c
## otherwise error will occur "no such file or directory"

bus = smbus2.SMBus(1)

while True:

  bus.write_i2c_block_data(0x44, 0x2C, [0x06])

  time.sleep(0.6)

  data = bus.read_i2c_block_data(0x44, 0x00, 6)

  temperature = data[0] * 256 + data[1]
  tempConv = -45 + (175 * temperature / 65535.0)
  humConv = 100 * (data[3] * 256 + data[4]) / 65535.0

  print ("Temp: %.2f C" %tempConv)
  print ("Hum: %.2f %%\n" %humConv)

  time.sleep(5)
