#!/bin/python3

import os
from gpiozero import LED

light = LED(24)

light.on()

os.system('raspistill -q 100 -br 50 -rot 270 -roi 0,0.1,0.8,0.8 -w 500 -h 500 -n -o /mnt/terraControl/view.jpg')

light.off()

