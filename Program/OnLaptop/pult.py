#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from RTCJoystick import Joystick
from Control import Control
from config import *
import time
import GstCV

joystick = Joystick()
joystick.connect("/dev/input/js0")
joystick.info()

control = Control()
control.setJoystick(joystick)
control.robot.connect(IP, str(PORT))

joystick.start()
control.start()

camera = GstCV.CVGstreamer(IP, 5000, 5001, 5005, toAVS=True, codec="JPEG")
camera.start()

while True:
    time.sleep(0.5)
