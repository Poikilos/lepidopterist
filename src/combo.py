#!/usr/bin/env python3
'''
Set combos.

The rule is: two keys are a combo.
'''
import sys
import pygame
from pygame.locals import *
from controller import (
    Controller,
    set_controllers_verbose,
)
from controls import (
    controller1,
    get_button_if_exists,
    read_joysticks,
    read_event,
)

watched = ('jump', 'x<0', 'x>0', 'nab')
waspressed = dict((k, False) for k in watched)
combokeys = set()
combostart = None

combodict = {}
def addcombo(keys, name):
    combodict[tuple(sorted(keys))] = name

addcombo(('nab',), "nab")  # formerly K_SPACE
addcombo(('jump',), "leap")  # formerly K_UP
addcombo(('x<0',), "turn-r")  # formerly K_LEFT
addcombo(('x>0',), "turn-l")  # formerly K_RIGHT
# ^ Why they are opposite: turning in mid-air is the combo
addcombo(('jump', 'nab'), "twirl")  # formerly (K_UP, K_SPACE)
addcombo(('x>0', 'nab'), "roll-r")  # formerly (K_RIGHT, K_SPACE)
addcombo(('x<0', 'nab'), "roll-l")  # formerly (K_LEFT, K_SPACE)
addcombo(('x>0', 'y<0'), "dart-r")  # formerly (K_RIGHT, K_UP)
addcombo(('x<0', 'y<0'), "dart-l")  # formerly (K_LEFT, K_UP)
# ^ bound and dart are opposites
#   - See feat.py


from enum import Enum


def error(msg):
    sys.stderr.write("{}\n".msg)


def equalsPart(list1, list2):
    count = int(min(len(list1), len(list2)))
    for i in range(count):
        if list1[i] is not list2[i]:
            return False
    return True


def get_combo(controller1):
    global waspressed, combokeys, combostart

    ispressed = dict((k, controller1.getBool(k)) for k in watched)
    newkeys = [k for k in watched if ispressed[k] and not waspressed[k]]
    r = ()
    if combokeys:
        # print("combokeys:{}".format(combokeys))
        if not all(controller1.getBool(k) for k in combokeys):  # End the combo now
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
        for event in pygame.event.get():
            result = 0
            if event.type == QUIT:
                sys.exit()
            else:
                result = read_event(controller1, event)
        # k = pygame.key.get_pressed()
        # pressed = controller1.toKeys()
        # read_joysticks(controller1, joysticks)
        # k = controller1.toKeys()
        kcombo = get_combo(controller1)
        if kcombo:
            print(kcombo)
        if controller1.getBool('EXIT'):
            sys.exit()

