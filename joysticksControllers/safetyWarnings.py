#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2024, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
# Notice
#   1. Changes to this file on Studio will not be preserved
#   2. The next conversion will overwrite the file with the same name
"""
import sys
import math
import time
import datetime
import random
import traceback
import threading
import subprocess
import pygame



XarmMaxX = 430
XarmMinX = -430
XarmMaxY = 410
XarmMinY = -410
XarmMinZ = 210
XarmMaxZ = 550


XarmCurrentX = 0
XarmCurrentY = 0
XarmCurrentZ = 0


try:
    from xarm.tools import utils
except:
    pass
from xarm import version
from xarm.wrapper import XArmAPI

def pprint(*args, **kwargs):
    try:
        stack_tuple = traceback.extract_stack(limit=2)[0]
        print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
    except:
        print(*args, **kwargs)

pprint('xArm-Python-SDK Version:{}'.format(version.__version__))

arm = XArmAPI('10.2.172.20')
arm.clean_warn()
arm.clean_error()
arm.motion_enable(True)
arm.set_mode(0)
arm.set_state(0)
time.sleep(1)

variables = {}
params = {'speed': 100, 'acc': 2000, 'angle_speed': 20, 'angle_acc': 500, 'events': {}, 'variables': variables, 'callback_in_thread': True, 'quit': False}


# Register error/warn changed callback
def error_warn_change_callback(data):
    if data and data['error_code'] != 0:
        params['quit'] = True
        pprint('err={}, quit'.format(data['error_code']))
        arm.release_error_warn_changed_callback(error_warn_change_callback)
arm.register_error_warn_changed_callback(error_warn_change_callback)


# Register state changed callback
def state_changed_callback(data):
    if data and data['state'] == 4:
        if arm.version_number[0] > 1 or (arm.version_number[0] == 1 and arm.version_number[1] > 1):
            params['quit'] = True
            pprint('state=4, quit')
            arm.release_state_changed_callback(state_changed_callback)
arm.register_state_changed_callback(state_changed_callback)


# Register counter value changed callback
if hasattr(arm, 'register_count_changed_callback'):
    def count_changed_callback(data):
        if not params['quit']:
            pprint('counter val: {}'.format(data['count']))
    arm.register_count_changed_callback(count_changed_callback)


# Register connect changed callback
def connect_changed_callback(data):
    if data and not data['connected']:
        params['quit'] = True
        pprint('disconnect, connected={}, reported={}, quit'.format(data['connected'], data['reported']))
        arm.release_connect_changed_callback(error_warn_change_callback)
arm.register_connect_changed_callback(connect_changed_callback)

subprocess.Popen(['python', '../playmp3.py', '../XarmVoices\Control_EN_sentence_1.mp3'])

if arm.error_code == 0 and not params['quit']:

    

    try:

        spoken = False

        while True:
            current_angles = arm.get_servo_angle()
            current_positions = arm.get_position()
            #print(current_positions)

            currentY = current_positions[1][1]
            currentX = current_positions[1][0]
            currentZ = current_positions[1][2]

            errorMessage = ""


            if (currentY > XarmMaxY-20 or currentY < XarmMinY+20 or currentX > XarmMaxX-20 or currentX < XarmMinX+20) :
                errorMessage = "../XarmVoices\Control_EN_sentence_2.mp3"
            if (currentY > -170  and  currentY < 170 and currentX < 200 and  currentX > -250 ) :
                errorMessage = "../XarmVoices\BASIC_EN_sentence_1.mp3"
            if (currentZ < XarmMinZ+10):
                errorMessage = "../XarmVoices\Control_EN_sentence_5.mp3"
            if (currentZ > XarmMaxZ-10):
                errorMessage = "../XarmVoices\Control_EN_sentence_4.mp3"
 
            if (errorMessage != "" and spoken == False) :
                subprocess.Popen(['python', '../playmp3.py', errorMessage])
                spoken = True
            
            if (spoken == True and errorMessage == "") :
                spoken = False
           
            time.sleep(0.1)


    except KeyboardInterrupt:
        print("Programma gestopt door gebruiker.")

# release all event
if hasattr(arm, 'release_count_changed_callback'):
    arm.release_count_changed_callback(count_changed_callback)
arm.release_error_warn_changed_callback(state_changed_callback)
arm.release_state_changed_callback(state_changed_callback)
arm.release_connect_changed_callback(error_warn_change_callback)
