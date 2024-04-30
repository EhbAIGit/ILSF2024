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

import pygame


XarmInitialX = 250
XarmInitialY = 0
XarmInitialZ = 260

XarmMaxX = 430
XarmMinX = -430
XarmMaxY = 410
XarmMinY = -405
XarmMinZ = 210
XarmMaxZ = 550


lastX = XarmInitialX
lastY = XarmInitialY
lastZ = XarmInitialZ



XarmCurrentX = XarmInitialX
XarmCurrentY = XarmInitialY
XarmCurrentZ = XarmInitialZ





# Initialiseer pygame en de joystick
pygame.init()
pygame.joystick.init()


# Controleer of er joysticks zijn aangesloten
if pygame.joystick.get_count() == 0:
    print("Geen joystick gevonden.")
    quit()

# Selecteer de eerste joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

"""
# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK
# git clone git@github.com:xArm-Developer/xArm-Python-SDK.git
# cd xArm-Python-SDK
# python setup.py install
"""
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

if arm.error_code == 0 and not params['quit']:

    code = arm.set_position(*[XarmInitialX, XarmInitialY, XarmInitialZ, 180.0, 0.0, 0.0], speed=params['speed'], mvacc=params['acc'], radius=-1.0, wait=True)


    try:
        while True:
            pygame.event.pump()

            

            # Lees de invoer van de joystick uit
            y2_axis = joystick.get_axis(0)  
            y_axis = joystick.get_axis(2)*-1  # X-as
            x_axis = joystick.get_axis(3)*-1  # Y-as
            Buttons = [joystick.get_button(0),joystick.get_button(1),joystick.get_button(2),joystick.get_button(3)]
            Thumb_x = joystick.get_hat(0)[0]
            Thumb_y = joystick.get_hat(0)[1]
            # Print de joystickgegevens
            #print("X-as: {:.2f}, Y-as: {:.2f}, Button3:{}, Hat(x-y):{}-{}".format(x_axis, y_axis,y2_axis,Buttons,Thumb_x, Thumb_y))

            if (x_axis>0.1) :  
                XarmCurrentX = XarmCurrentX + abs(x_axis*100)
                if (XarmCurrentX > XarmMaxX ) : 
                    XarmCurrentX = XarmCurrentX - abs(x_axis*100)
            if (x_axis<-0.1) :  
                XarmCurrentX = XarmCurrentX - abs(x_axis*100)
                if (XarmCurrentX < XarmMinX ) : 
                    XarmCurrentX = XarmCurrentX + abs(x_axis*100)
            if (y_axis>0.1) :  
                XarmCurrentY = XarmCurrentY + abs(y_axis*100)
                if (XarmCurrentY > XarmMaxY ) : 
                    XarmCurrentY = XarmCurrentY - abs(y_axis*100)
            if (y_axis<-0.1) :  
                XarmCurrentY = XarmCurrentY - abs(y_axis*100)
                if (XarmCurrentY < XarmMinY ) : 
                    XarmCurrentY = XarmCurrentY + abs(y_axis*100)
            if (Thumb_y==-1) :  
                XarmCurrentZ = XarmCurrentZ - 10
                if (XarmCurrentZ < XarmMinZ ) : 
                    XarmCurrentZ = XarmMinZ
            if (Thumb_y==1) :  
                XarmCurrentZ = XarmCurrentZ + 10
                if (XarmCurrentZ > XarmMaxZ ) : 
                    XarmCurrentZ = XarmMaxZ

            if (Buttons[0] == 1) :
                code = arm.set_cgpio_analog(0, 5)
            elif (Buttons[3] == 1):
                code = arm.set_cgpio_analog(0, 0)
            if (Buttons[1] == 1) :
                code = arm.playback_trajectory(times=1, filename='exterior_pattern', wait=True)           
            if (Buttons[2] == 1) :
                code = arm.set_position(*[XarmInitialX, XarmInitialY, XarmInitialZ, 180.0, 0.0, 0.0], speed=params['speed'], mvacc=params['acc'], radius=-1.0, wait=True)          
            
            if (y2_axis > 0.5) :
                current_angles = arm.get_servo_angle()
                currentAngle = current_angles[1][5] - 10
                current_angles[1][5] = currentAngle
                if (current_angles[1][5] < -46 ) :
                    current_angles[1][5] = -46
                code = arm.set_servo_angle(angle=current_angles[1], speed=params['angle_speed'], mvacc=params['angle_acc'], wait=True, radius=-1.0)
            if (y2_axis < -0.5) :
                current_angles = arm.get_servo_angle()
                currentAngle = current_angles[1][5] + 10
                current_angles[1][5] = currentAngle
                if (current_angles[1][5] > 46 ) :
                    current_angles[1][5] = 46
                code = arm.set_servo_angle(angle=current_angles[1], speed=params['angle_speed'], mvacc=params['angle_acc'], wait=True, radius=-1.0)


            
        
            if (lastX != XarmCurrentX or lastY!= XarmCurrentY or lastZ!= XarmCurrentZ) : 
                #print ("new X-as: {} Y-As: {}, Z-As: {} ".format(XarmCurrentX,XarmCurrentY,XarmCurrentZ))
                #print ("new X-as: {}".format(XarmCurrentX))
                code = arm.set_position(*[XarmCurrentX, XarmCurrentY, XarmCurrentZ, 180.0, 0.0, 0.0], speed=params['speed'], mvacc=params['acc'], radius=-1.0, wait=True)
                
            lastX = XarmCurrentX
            lastY = XarmCurrentY
            lastZ = XarmCurrentZ 

            current_angles = arm.get_servo_angle()
            #print (current_angles)
            #time.sleep(0.25) 


    except KeyboardInterrupt:
        print("Programma gestopt door gebruiker.")



    #code = arm.set_position(*[350.0, 0.0, 300, 180.0, 0.0, 0.0], speed=params['speed'], mvacc=params['acc'], radius=-1.0, wait=True)
    #time.sleep(1)

    if code != 0:
        params['quit'] = True
        pprint('set_position, code={}'.format(code))

# release all event
if hasattr(arm, 'release_count_changed_callback'):
    arm.release_count_changed_callback(count_changed_callback)
arm.release_error_warn_changed_callback(state_changed_callback)
arm.release_state_changed_callback(state_changed_callback)
arm.release_connect_changed_callback(error_warn_change_callback)
