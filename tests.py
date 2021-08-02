#!/usr/bin/env python

from src.controls import controller1
from src.controller import set_controllers_verbose
from pygame.locals import *

controller1.setHat(0, (1, 0))
assert(controller1.getInt('x') == 1)
assert(controller1.getInt('y') == 0)

controller1.setHat(0, (0, 1))
assert(controller1.getInt('x') == 0)
assert(controller1.getInt('y') == -1)
# ^ -1 since set invert_y to True when called addHat

controller1.clearPressed()
controller1.setKey(K_LEFT, True)
leftSID = controller1._kc_to_sid[str(K_LEFT)]
print("sid for K_LEFT: {}".format(leftSID))
print("  K_LEFT value: {}".format(controller1._kc_value[str(K_LEFT)]))
print("  leftSID state: {}".format(controller1._states[leftSID]))
print("  controller1.getInt('x'): {}".format(controller1.getInt('x')))
set_controllers_verbose(True)
assert(controller1.getInt('x') == -1)
assert(controller1.getInt('y') == 0)

controller1.clearPressed()
controller1.setKey(K_RIGHT, True)
assert(controller1.getInt('x') == 1)
assert(controller1.getInt('y') == 0)

controller1.clearPressed()
controller1.setKey(K_UP, True)
assert(controller1.getInt('x') == 0)
assert(controller1.getInt('y') == -1)

controller1.clearPressed()
controller1.setKey(K_DOWN, True)
assert(controller1.getInt('x') == 0)
assert(controller1.getInt('y') == 1)


controller1.clearPressed()
controller1.setKey(K_DOWN, True)
assert(controller1.getInt('x') == 0)
assert(controller1.getInt('y') == 1)

controller1.clearPressed()

print("controller1.getBool('SCREENSHOT'): {}"
      "".format(controller1.getBool('SCREENSHOT')))
# ^ a state must exist even before it is pressed.

gt_is_prevented = False
try:
    controller1.addKey(1000001, '>')
except ValueError:
    gt_is_prevented = True
assert(gt_is_prevented)

lt_is_prevented = False
try:
    controller1.addKey(1000002, '<')
except ValueError:
    lt_is_prevented = True
assert(lt_is_prevented)

controller1.clearPressed()
controller1.setKey(K_LEFT, True)
assert(controller1.getBool("x<0"))
assert(not controller1.getBool("x>0"))

controller1.clearPressed()
controller1.setKey(K_RIGHT, True)
assert(controller1.getBool("x>0"))
assert(not controller1.getBool("x<0"))

print("All tests passed.")
