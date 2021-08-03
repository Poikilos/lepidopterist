#!/usr/bin/env
'''
Keep track of available feats.
'''

import pygame, random
from pygame.locals import *
import vista, effect, settings, sprite

allfeats = ("nab", "leap", "turn", "twirl", "bound", "dart", "roll")

known = {}
known["nab"] = 2
known["leap"] = 1

if settings.cheat:
    known = dict((featK, 6) for featK in allfeats)

upgradecost = {}
upgradecost["nab"] = (5, 10, 30, 80, 200)
upgradecost["leap"] = (10, 20, 60, 140, 300)
upgradecost["turn"] = (20, 50, 120, 280, 400)
upgradecost["twirl"] = (80, 200, 450, 800, 2000)
upgradecost["bound"] = (80, 200, 450, 800, 2000)
upgradecost["dart"] = (80, 200, 450, 800, 2000)
upgradecost["roll"] = (200, 500, 2000, 5000, 20000)

keys = {}
keys["nab"] = ("return",)  # formerly ("sp",)
keys["leap"] = ("sp",)  # formerly ("up",)
keys["turn"] = ("back",)  # formerly ("back",)
keys["twirl"] = ("sp", "return")  # formerly ("up", "sp")
keys["bound"] = ("sp", "back")  # formerly ("up", "back")
keys["dart"] = ("sp", "forward")  # formerly ("up", "forward")
keys["roll"] = ("forward", "return")  # formerly ("forward", "sp")

learnat = (0, 2, 4, 6, 8, 10, 999)

def growtime(n, nmax):
    return 2. + 0.5 * (nmax - n)

def startlevel(fillbars = True):
    global bars, feattick, feateffects, currentfeattick
    if fillbars: bars = dict(known)
    feattick = dict((featname, 0) for featname in known)
    feateffects = {}
    for featname in allfeats:
        if featname in known:
            name = featname
            feateffects[featname] = effect.FeatIndicator(name, len(feateffects))
    for ffx in list(feateffects.values()):
        ffx.position(vista.screen)
    currentfeattick = 0

def attempt(featname):
    global currentfeat, currentfeattick
    if featname not in known:
        return False
    if not bars[featname]:
        return False
    bars[featname] -= 1
    feattick[featname] = growtime(bars[featname], known[featname])
    currentfeat, currentfeattick = featname, 0.4
    return True

def think(dt):
    global currentfeattick
    for featname in known:
        if feattick[featname]:
            feattick[featname] = max(feattick[featname] - dt, 0)
            if not feattick[featname]:
                bars[featname] += 1
                if bars[featname] < known[featname]:
                    feattick[featname] = growtime(bars[featname], known[featname])
    if currentfeattick:
        currentfeattick = max(currentfeattick - dt, 0)

shop_pos = (160, 60)

def draw(facingright = True, shopping = False):
    if shopping:
        img = pygame.surface.Surface((300, 250)).convert_alpha()
        img.fill((0,0,0,0))
        xoff, yoff = shop_pos
    else:
        img = vista.screen
        if settings.hidefeatnames:
            xoff, yoff = -105, 0
        else:
            xoff, yoff = 0, 0

    if currentfeattick and not settings.hidefeatnames:
        for n,featK in enumerate(allfeats):
            if featK == currentfeat:
                g = random.choice(("glow0", "glow1", "glow2", "glow3"))
                sprite.frames[g].place((110 - 11*len(featK), 25 + 32 * n))
    for n,featK in enumerate(allfeats):
        if featK not in known: continue
        if shopping or not settings.hidefeatnames:
            feateffects[featK].draw(img)
        kmap = dict((("return", "key-return"), ("sp", "key-space"),
                     ("forward", ("key-right" if facingright else "key-left")),
                     ("back", ("key-left" if facingright else "key-right"))))
        # ^ The values must exist in frames (See sprite.py)
        ks = keys[featK]
        if len(ks) == 2:
            sprite.frames[kmap[ks[0]]].place((115 + xoff, 24 + 32 * n + yoff))
            sprite.frames[kmap[ks[1]]].place((142 + xoff, 24 + 32 * n + yoff))
        else:
            try:
                sprite.frames[kmap[ks[0]]].place((128 + xoff, 24 + 32 * n + yoff))
            except KeyError as ex:
                raise KeyError(
                    "{}\n\n"
                    " kmap[ks[0]] {} may be missing from"
                    " frames in sprite.py (ks[0]:{})"
                    "".format(
                        ex,
                        ks[0],  # such as 'return'
                        kmap[ks[0]],  # such as 'key-return'
                    )
                )

        for j in range(known[featK]):
            if shopping or not settings.hidefeatnames:
                r = pygame.Rect((160 + 20 * j), (12 + 32 * n), 16, 20)
            else:
                r = pygame.Rect((52 + 8 * j), (12 + 32 * n), 8, 20)
            fill = (255, 0, 0) if j < bars[featK] else (0, 0, 0)
            pygame.draw.rect(img, fill, r)
            pygame.draw.rect(img, (255, 255, 255), r, 2)
    if shopping:
        vista.screen.blit(img, (xoff, yoff))


def land():
    for featK in known:
#        if featK != "nab":
            bars[featK] = known[featK]
            feattick[featK] = 0

def getupgradecost(featname):
    ucost = upgradecost[featname]
    if known[featname] > len(ucost):
        return 0
    else:
        return ucost[known[featname] - 1]

def checknewfeat(ncaught):
    if len(known) >= len(allfeats):
        return []
    newfeat = []
    while ncaught >= learnat[len(known) - 1]:
        known[allfeats[len(known)]] = 1
        newfeat = ["You learned a|new ability!"]
    if newfeat:
        startlevel()
    return newfeat


