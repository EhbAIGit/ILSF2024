#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
Description: Move Joint
"""

#include "xarm/wrapper/xarm_api.py"


import os
import sys
import time
import math

from xarm.wrapper import XArmAPI


#######################################################
"""
Just for test example
"""
if len(sys.argv) >= 2:
    ip = "10.2.172.20"
else:
    try:
        from configparser import ConfigParser
        parser = ConfigParser()
        parser.read('robot.conf')
        ip = "10.2.172.20"
    except:
        ip = input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
########################################################


arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

arm.reset(wait=True)

speed = 50
arm.set_servo_angle(angle=[2, 33.9, 47.3, 68.2, -37.1, 32.8,1.1], speed=speed, wait=True)
print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=True))
arm.reset(wait=True)
arm.disconnect()
