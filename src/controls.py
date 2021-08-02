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
# controller1.addKey(1, Button.FEAT)
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


def read_joysticks(controller, joysticks):
    for joystick in joysticks:
        for i in range(joystick.get_numbuttons()):
            sid = controller1._btn_to_sid.get(str(i))
            if sid is None:
                continue
            value = joystick.get_button(i)
            controller1.setButton(i, value)
        for i in range(joystick.get_numhats()):
            sids = controller1._hat_to_sids.get(str(i))
            if sids is None:
                continue
            values = joystick.get_hat(i)
            # sid0, sid1 = sids
            controller1.setHat(i, values)
        for i in range(joystick.get_numaxes()):
            sid = controller1._btn_to_sid.get(str(i))
            if sid is None:
                continue
            value = joystick.get_axis(i)
            controller1.setAxis(i, value)

def get_button_if_exists(joystick, button):
    if button < joystick.get_numbuttons():
        return joystick.get_button(button)
    return False

def read_event(thisController, event):
    '''
    Update the controller using the event.

    Returns:
    1 controller changed, 2 if hat down, 3 if button down, 0 if not
    changed (neither up nor down)
    '''
    if event.type == KEYDOWN:
        thisController.setKey(event.key, True)
        return 3
    elif event.type == KEYUP:
        thisController.setKey(event.key, False)
        return 1
    elif event.type == JOYBUTTONDOWN:
        thisController.setButton(event.button, True)
        return 3
    elif event.type == JOYBUTTONUP:
        thisController.setButton(event.button, False)
        return 1
    elif event.type == JOYHATMOTION:
        # NOTE: joy is deprecated. Use instanceid
        # (See <https://www.pygame.org/docs/ref/event.html>):
        # joyI = event.instanceid
        thisController.setHat(event.hat, event.value)
        if (event.value[0] != 0) or (event.value[1] != 0):
            return 2
        return 1
    elif event.type == JOYAXISMOTION:
        thisController.setAxis(event.axis, event.value)
        return 1

    return 0
