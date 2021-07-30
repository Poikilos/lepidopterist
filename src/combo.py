#!/usr/bin/env
'''
Set combos.

The rule is: two keys are a combo.
'''

import pygame
from pygame.locals import *

watched = (K_UP, K_LEFT, K_RIGHT, K_SPACE)
waspressed = dict((k, False) for k in watched)
combokeys = set()
combostart = None

combodict = {}
def addcombo(keys, name):
    combodict[tuple(sorted(keys))] = name

addcombo((K_SPACE,), "nab")
addcombo((K_UP,), "leap")
addcombo((K_LEFT,), "turn-r")
addcombo((K_RIGHT,), "turn-l")
addcombo((K_UP, K_SPACE), "twirl")
addcombo((K_RIGHT, K_SPACE), "roll-r")
addcombo((K_LEFT, K_SPACE), "roll-l")
addcombo((K_RIGHT, K_UP), "dart-r")
addcombo((K_LEFT, K_UP), "dart-l")  # bound and dart are opposites

pressed = None
show_joystick_stats = False

def get_button_if_exists(joystick, index):
    if index < joystick.get_numbuttons():
        return joystick.get_button(index)
    return False

def soft_input(k, joysticks):
    global pressed
    global show_joystick_stats
    if pressed is None:
        pressed = [v for v in k]
    else:
        for i in range(len(k)):
            pressed[i] = k[i]
    if joysticks is None:
        print("[soft_input] There are no joysticks.")
        show_joystick_stats = False
        return pressed
    buttonJump = 2  # use the inside of the thumb joint
    # ^ 3 is labeled as "4" on Saitek 14-button
    # ^ 2 is labeled as "3"
    buttonNab = 0  # use the tip of the thumb
    # ^ 1 is labeled as "2" on Saitek 14-button and so
    # ^ 0 is labeled as "1"
    buttonBack = 3
    buttonFeat = 1
    buttonPause = 4
    buttonFullscreen = 5
    for joystickI in range(len(joysticks)):
        joystick = joysticks[joystickI]
        if show_joystick_stats:
            print("* joystick {}".format(joystickI))
        if joystick.get_numaxes() >= 2:
            axisX = 0
            axisY = 1
            # Use a dead zone since axes are (or appear as) analog.
            x = joystick.get_axis(axisX)
            y = joystick.get_axis(axisY)
            deadZone = .2
            if x < -deadZone:
                if show_joystick_stats:
                    print("joystick axis {} left".format(axisX))
                pressed[K_LEFT] = True
            elif x > deadZone:
                if show_joystick_stats:
                    print("joystick axis {} right".format(axisX))
                pressed[K_RIGHT] = True
            if y < -deadZone:
                if show_joystick_stats:
                    print("joystick axis {} down".format(axisY))
                pressed[K_DOWN] = True
            elif y > deadZone:
                if show_joystick_stats:
                    print("joystick axis {} up".format(axisY))
                pressed[K_UP] = True
        else:
            if show_joystick_stats:
                print("  * There are only {} axes."
                      "".format(joystick.get_numaxes()))

        if joystick.get_numhats() >= 1:
            hatI = 0
            x, y = joystick.get_hat(hatI)
            if x < 0:
                if show_joystick_stats:
                    print("joystick hat {} left".format(hatI))
                pressed[K_LEFT] = True
            elif x > 0:
                if show_joystick_stats:
                    print("joystick hat {} right".format(hatI))
                pressed[K_RIGHT] = True
            if y < 0:
                if show_joystick_stats:
                    print("joystick hat {} down".format(hatI))
                pressed[K_DOWN] = True
            elif y > 0:
                if show_joystick_stats:
                    print("joystick hat {} up".format(hatI))
                pressed[K_UP] = True
        else:
            if show_joystick_stats:
                print("  * There are only {} hats."
                      "".format(joystick.get_numhats()))

        if joystick.get_numbuttons() >= 2:
            if joystick.get_numbuttons() == 2:
                if buttonJump >= 2:
                    tmp = buttonJump
                    buttonJump = buttonFeat
                    buttonFeat = tmp
            if get_button_if_exists(joystick, buttonJump):
                pressed[K_UP] = True
            if get_button_if_exists(joystick, buttonNab):
                pressed[K_SPACE] = True
            if get_button_if_exists(joystick, buttonFeat):
                pressed[K_TAB] = True
            if get_button_if_exists(joystick, buttonPause):
                pressed[K_ESC] = True
            if get_button_if_exists(joystick, buttonFullscreen):
                pressed[K_f] = True
            pass
        if show_joystick_stats:
            print("  * There are {} buttons."
                  "".format(joystick.get_numbuttons()))
    show_joystick_stats = False
    return pressed


def check_input(pressed):
    global waspressed, combokeys, combostart

    ispressed = dict((k, pressed[k]) for k in watched)
    newkeys = [k for k in watched if ispressed[k] and not waspressed[k]]
    r = ()
    if combokeys:
        if not all(pressed[k] for k in combokeys):  # End the combo now
            r = combokeys
            if newkeys:
                combokeys = set(newkeys)
                combostart = pygame.time.get_ticks()
            else:
                combokeys = set()
                combostart = None
        elif newkeys:
            combokeys |= set(newkeys)
        if combokeys and pygame.time.get_ticks() - combostart > 100:  # Combo timed out
            r = combokeys
            combokeys = set()
            combostart = None
    elif newkeys:
        combokeys = set(newkeys)
        combostart = pygame.time.get_ticks()
    waspressed = ispressed
    r = tuple(sorted(r))
    return combodict[r] if r in combodict else ""

if __name__ == "__main__":
    global show_joystick_stats
    show_joystick_stats = True
    # Go to a module test mode if the module runs directly.
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    print("Pygame found {} joystick(s).".format(len(joysticks)))
    if len(joysticks) > 0:
        for joystick in joysticks:
            joystick.init()
    pygame.display.set_mode((800, 300))
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) * 0.001
        pygame.event.get()
        k = pygame.key.get_pressed()
        pressed = soft_input(k, joysticks)
        kcombo = check_input(pressed)
        if kcombo:
            print(kcombo)
        if k[K_ESCAPE]:
            exit()

