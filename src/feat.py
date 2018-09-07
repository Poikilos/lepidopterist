# System for keeping track of available feats

import pygame
from pygame.locals import *
import vista, effect

allfeats = ("nab", "leap", "turn", "twirl")

known = {}
known["nab"] = 3
known["leap"] = 3
known["twirl"] = 3

def growtime(n):
    return 2.

def startlevel():
    global bars, feattick, feateffects
    bars = dict(known)
    feattick = dict((featname, 0) for featname in known)
    feateffects = {}
    for featname in allfeats:
        if featname in known:
            name = featname
            feateffects[featname] = effect.FeatIndicator(name, len(feateffects))
    for f in feateffects.values():
        f.position(vista.screen)

def attempt(featname):
    if featname not in known:
        return False
    if not bars[featname]:
        return False
    bars[featname] -= 1
    feattick[featname] = growtime(bars[featname])
    return True
    
def think(dt):
    for featname in known:
        if feattick[featname]:
            feattick[featname] = max(feattick[featname] - dt, 0)
            if not feattick[featname]:
                bars[featname] += 1
                if bars[featname] < known[featname]:
                    feattick[featname] = growtime(bars[featname])

def draw():
    n = 0
    for f in allfeats:
        if f not in known: continue
        feateffects[f].draw(vista.screen)
        for j in range(known[f]):
            r = pygame.Rect((105 + 20 * j), (12 + 32 * n), 16, 20)
            fill = (255, 0, 0) if j < bars[f] else (0, 0, 0)
            pygame.draw.rect(vista.screen, fill, r)
            pygame.draw.rect(vista.screen, (255, 255, 255), r, 2)
        n += 1
    
def land():
    for f in known:
        if f != "nab":
            bars[f] = known[f]
            feattick[f] = 0


