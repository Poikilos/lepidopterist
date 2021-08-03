#!/usr/bin/env python3

from controller import (
    Controller,
    set_controllers_verbose,
)
from pygame.locals import *

# desired controls:
# - The set below allows middle of thumb to press jump and pad of thumb
#   to press nab on controllers such as Saitek with the following
#   layout:
#       2
#    1     4
#       3
#   which the computer reads as:
#       1
#    0     3
#       2
# The desired zero-indexed values are as follows:
# NAB = 0
# FEAT = 1  # toggle the feat name display
# JUMP = 2
# BACK = 3
# PAUSE = 4
# FULLSCREEN = 5
# SCREENSHOT = 6

# Old Controls:
# - K_SPACE: 'nab'
# - K_TAB: toggle feat display
# - K_UP: 'leap' combo; increase an amount in menu
# - K_LEFT
# - K_RIGHT
# - K_DOWN: decrease an amount in menu

# DOCUMENTATION: Ensure that the instructions in the "CONTROLS" section
# of the readme match this file.

# capitalized ones are not related to controlling the character:
controller1 = Controller()
controller1.addKeyAsAxisValue(K_LEFT, 'x', -1)
controller1.addKeyAsAxisValue(K_RIGHT, 'x', 1)
controller1.addKeyAsAxisValue(K_UP, 'y', -1)
controller1.addKeyAsAxisValue(K_DOWN, 'y', 1) # for menus  & "easy mode"
controller1.addKeyAsAxisValue(K_a, 'x', -1)
controller1.addKeyAsAxisValue(K_d, 'x', 1)
controller1.addKeyAsAxisValue(K_w, 'y', -1)
controller1.addKeyAsAxisValue(K_s, 'y', 1)
controller1.addKey(K_RETURN, 'nab')  # formerly K_SPACE
controller1.addKey(K_TAB, 'feat')
controller1.addKey(K_SPACE, 'jump')  # formerly K_UP; combo is 'leap'
controller1.addKey(K_BACKSPACE, 'BACK')
controller1.addKey(K_ESCAPE, 'EXIT')
controller1.addKey(K_f, 'FULLSCREEN')
controller1.addKey(K_F12, 'SCREENSHOT')

controller1.addButton(0, 'nab')  # get a butterfly; confirm in menu
controller1.addButton(1, 'feat')  # originally K_TAB; toggle feat names
controller1.addButton(2, 'jump')  # originally K_UP
controller1.addButton(3, 'BACK')  # originally K_BACKSPACE
controller1.addButton(4, 'EXIT')  # originally K_ESCAPE; also for pause
controller1.addButton(5, 'FULLSCREEN')  # originally K_f
controller1.addButton(6, 'SCREENSHOT')  # originally K_F12

controller1.addAxis(0, 'x')  # joystick axis 0 affects dir x
controller1.addAxis(1, 'y')  # joystick axis 1 affects dir y
controller1.addHat(0, ('x', 'y'), True)  # hat 0[0],0[1] affects x,y
# ^ Down is positive, up is negative (invert hats to match analog axes)

_gamepad_used = False

def gamepad_used():
    return _gamepad_used

'''
def read_joysticks(thisController, joysticks):
    global _gamepad_used
    for joystick in joysticks:
        for i in range(joystick.get_numbuttons()):
            sid = thisController._btn_to_sid.get(str(i))
            if sid is None:
                continue
            value = joystick.get_button(i)
            thisController.setButton(i, value)
            if value > 0:
                _gamepad_used = True
        for i in range(joystick.get_numhats()):
            sids = thisController._hat_to_sids.get(str(i))
            if sids is None:
                continue
            values = joystick.get_hat(i)
            # sid0, sid1 = sids
            thisController.setHat(i, values)
        for i in range(joystick.get_numaxes()):
            sid = thisController._btn_to_sid.get(str(i))
            if sid is None:
                continue
            value = joystick.get_axis(i)
            thisController.setAxis(i, value)
'''

def get_button_if_exists(joystick, button):
    global _gamepad_used
    if button < joystick.get_numbuttons():
        if joystick.get_button(button) > 0:
            _gamepad_used = True
        return joystick.get_button(button)
    return False

_last_read_actuator_info = {}

def last_read_actuator_info():
    return _last_read_actuator_info

def read_event(thisController, event):
    '''
    Update the controller using the event.

    Returns:
    1 controller changed, 2 if hat down, 3 if button down, 0 if not
    changed (neither up nor down)
    '''
    global _gamepad_used
    global _last_read_actuator_info
    _last_read_actuator_info = {}
    if event.type == KEYDOWN:
        thisController.setKey(event.key, True)
        _last_read_actuator_info['event.type'] = "KEYDOWN"
        _last_read_actuator_info['event.key'] = event.key
        return 3
    elif event.type == KEYUP:
        _last_read_actuator_info['event.type'] = "KEYUP"
        _last_read_actuator_info['event.key'] = event.key
        thisController.setKey(event.key, False)
        return 1
    elif event.type == JOYBUTTONDOWN:
        _last_read_actuator_info['event.type'] = "JOYBUTTONDOWN"
        _last_read_actuator_info['event.button'] = event.button
        thisController.setButton(event.button, True)
        _gamepad_used = True
        return 3
    elif event.type == JOYBUTTONUP:
        _last_read_actuator_info['event.type'] = "JOYBUTTONUP"
        _last_read_actuator_info['event.button'] = event.button
        thisController.setButton(event.button, False)
        return 1
    elif event.type == JOYHATMOTION:
        # NOTE: joy is deprecated. Use instanceid
        # (See <https://www.pygame.org/docs/ref/event.html>):
        # joyI = event.instanceid
        _last_read_actuator_info['event.type'] = "JOYHATMOTION"
        _last_read_actuator_info['event.hat'] = event.hat
        _last_read_actuator_info['event.value'] = event.value
        thisController.setHat(event.hat, event.value)
        if (event.value[0] != 0) or (event.value[1] != 0):
            _gamepad_used = True
            return 2
        return 1
    elif event.type == JOYAXISMOTION:
        _last_read_actuator_info['event.type'] = "JOYAXISMOTION"
        _last_read_actuator_info['event.axis'] = event.axis
        _last_read_actuator_info['event.value'] = event.value
        prevValue = thisController._getHWAxis(event.axis)
        prevOut = thisController.isPastDeadZone(prevValue)
        moved = thisController.setAxis(event.axis, event.value)
        nowValue = thisController._getHWAxis(event.axis)
        nowOut = thisController.isPastDeadZone(nowValue)
        if nowOut:
            _gamepad_used = True
        if prevOut is not nowOut:
            print("axis {} changed to {}".format(event.axis, nowOut))
        # else:
        #     print("axis {} was already {} at {} (raw:{})".format(event.axis, nowOut, nowValue, event.value))

        if moved > 0:
            # The axis moved out of the deadZone.
            if prevOut is not nowOut:
                # only return a change if moved and wasn't moved before
                return 2
            else:
                return 1
        elif moved < 0:
            # The axis isn't mapped.
            return 0
        else:
            # The movement isn't past the deadZone.
            return 0

    return 0
