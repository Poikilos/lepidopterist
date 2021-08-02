# -*- coding: utf-8 -*-
# Graphic text effects

import pygame, pickle, os
from pygame.locals import *
import data, vista, noise

fontcache = {}
imgcache = {}

# Replace "LLL" in effect string with the pounds sign
def addcurrency(s):
    if "LLL" not in s: return s
#    return s.replace("LLL", "£")    # Uncomment for Windows version
    return str(s).replace("LLL", u"\u00A3")

def savecache():
    return
    d = [(key, value.get_size(), pygame.image.tostring(value, "RGBA")) for key, value in list(imgcache.items())]
    pickle.dump(d, open(icachefile, "wb"))

class Effect(object):
    fontsize0 = 120
    fontname0 = "fightingspirit"
    expiring = True
    color0 = 255, 128, 0
    color1 = 255, 255, 0
    bratio = 32
    _verbose = False

    def __init__(self, texts, fontsize = None, fontname = None):
        self.expiring = self.__class__.expiring
        # self._verbose = self.__class__._verbose
        self.age = 0

        if fontsize is None: fontsize = self.fontsize0
        if fontname is None: fontname = self.fontname0
        self.fontsize = fontsize
        self.fontname = fontname
        key = self.fontname, self.fontsize
        if key not in fontcache:
            fpath = data.filepath("%s.ttf" % self.fontname) if self.fontname is not None else None
            fontcache[key] = pygame.font.Font(fpath, self.fontsize)
        self.font = fontcache[key]
        self.texts = list(texts)
        self.render()

    def set_verbose(self, verbose):
        self._verbose = verbose

    def debug(self):
        result = ""
        result += str(self)
        result += "; " + str(dir(self))
        result += "; expiring:" + str(self.expiring)
        result += "; age:" + str(self.age)
        result += "; __class__:" + str(self.__class__)
        result += "; texts:" + str(self.texts)
        return result

    def render(self):
        key = self.texts[0], self.fontname, self.fontsize, self.color0, self.color1
        if key in imgcache:
            self.image = imgcache[key]
        else:
            lines = self.texts[0].split("|")
            def renderlines(color):
                imgs = [self.font.render(addcurrency(line), True, color) for line in lines]
                if len(lines) == 1: return imgs[0]
                w = max(img.get_width() for img in imgs)
                h = sum(img.get_height() for img in imgs)
                timg = pygame.Surface((w,h)).convert_alpha()
                timg.fill((0,0,0,0))
                h = 0
                for img in imgs:
                    r = img.get_rect()
                    r.midtop = w/2, h
                    timg.blit(img, r)
                    h += img.get_height()
                return timg
            self.image0 = renderlines(self.color0)
            self.image1 = renderlines(self.color1)
            d = self.fontsize / self.bratio
            self.image = pygame.Surface((self.image0.get_width() + 2*d, self.image0.get_height() + 2*d)).convert_alpha()
            self.image.fill((0,0,0,0))
            self.image.blit(self.image1, (0,0))
            self.image.blit(self.image1, (0,2*d))
            self.image.blit(self.image1, (2*d,0))
            self.image.blit(self.image1, (2*d,2*d))
            self.image.blit(self.image0, (d,d))
            imgcache[key] = self.image
        self.rect = self.image.get_rect()
        self.age = 0

    def duration(self, n):
        return 0.5 + 0.05 * n

    def think(self, dt):
        if self._verbose:
            print("think (class:{})".format(self.__class__))
        if self._verbose is None:
            print("Error: self._verbose is None")
        if not self.texts:
            if self._verbose:
                print("self.texts is {}. self.__bool__ is {}"
                      "".format(bool(self.texts), self.__bool__()))
            return
        # if self._verbose:
        #     print("  texts: {}".format(self.texts))
        self.age += dt
        if not self.expiring:
            return
        if self.age > self.duration(len(self.texts[0])):
            self.advance()
        if self._verbose:
            print("  age: {}".format(self.age))

    def advance(self):
        self.age -= self.duration(len(self.texts[0]))
        del self.texts[0]
        if self.texts: self.render()

    def position(self, surf):
        self.rect.center = surf.get_rect().center

    def draw(self, surf):
        if not self.texts: return
        self.position(surf)
        surf.blit(self.image, self.rect)

    def __bool__(self):
        if self.texts and self._verbose:
            print("type {} self.texts: {}"
                  "".format(self.__class__, self.texts))
        return bool(self.texts)

class EndEffect(Effect):
    fontsize0 = 72
    fontname0 = "SFArchRival"
    def __init__(self, texts):
        self.n = 0
        Effect.__init__(self, texts)
    def render(self):
        if "incomplete" not in self.texts[0]:
            if self.n == 0:
                noise.play("win-1")
            elif self.n == 1:
                noise.play("win-2")
            else:
                noise.play("win-3")
            self.n += 1
        Effect.render(self)

class StageNameEffect(Effect):
    fontsize0 = 60
    fontname0 = "freesansbold"
    color0 = 128, 128, 255
    color1 = 0, 0, 0

    def __init__(self, levelnum, goal, timeout):
        levelname = "Stage %s" % levelnum if levelnum < 6 else "Final Stage"
        goaltext = "Get LLL%s in %s seconds" % (goal, timeout)
        Effect.__init__(self, [levelname, goaltext])

class EasyModeIndicator(Effect):
    fontsize0 = 40
    fontname0 = "KoolBean"
    color0 = 255, 255, 128
    color1 = 0, 0, 0

class Dialogue(Effect):
    fontsize0 = 28
    fontname0 = "Merkin"
    bratio = 18
    color1 = 255,255,255
    def __init__(self, line, who):
        if who == "m":
            self.color0 = 0,0,128
        elif who == "e":
            self.color0 = 128,128,0
        elif who == "s":
            self.color0 = 64,64,64
        elif who == "v":
            self.color0 = 0,128,0
        Effect.__init__(self, [line])
    def duration(self, n):
        return 1. + 0.06 * n
    def position(self, surf):
        self.rect.centerx = surf.get_rect().centerx
        self.rect.top = surf.get_rect().centery + 105

class Tip(Effect):
    fontsize0 = 40
    fontname0 = "SFArchRival"
    color0 = 0,0,128
    color1 = 255,255,255
    def duration(self, n):
        return 1. + 0.06 * n

class Credit(Effect):
    fontsize0 = 32
    fontname0 = "Merkin"
    color0 = 0,64,64
    color1 = 255,255,255
    def duration(self, n):
        return 2. + 0.005 * n

class PauseTitle(Effect):
    expiring = False

class TheEndTitle(Effect):
    expiring = False

class PauseInfo(Effect):
    fontname0 = "Merkin"
    fontsize0 = 32
    expiring = False
    color0 = 255,255,255
    color1 = 0,0,0
    def position(self, surf):
        self.rect.center = surf.get_rect().center
        self.rect.move_ip(0, 120)

class HighScoreTotal(Effect):
    fontname0 = "freesansbold"
    fontsize0 = 40
    expiring = False
    color0 = 255,255,255
    color1 = 0,0,0
    def position(self, surf):
        self.rect.center = surf.get_rect().center
        self.rect.move_ip(0, 120)

class AchievementEffect(Effect):
    fontsize0 = 54
    fontname0 = "SFArchRival"
    def __init__(self, texts):
        self.n = 0
        Effect.__init__(self, texts)
    def position(self, surf):
        self.rect.center = surf.get_rect().center
        self.rect.y += 120
    def render(self):
        if self.n == 0:
            noise.play("win-1")
        elif self.n == 1:
            noise.play("win-2")
        else:
            noise.play("win-3")
        self.n += 1
        Effect.render(self)

class CachedEffect(Effect):
    fontsize0 = 30
    fontname0 = "freesansbold"
    expiring = False
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self, text):
        self.icache = {}
        Effect.__init__(self, [text])
    def render(self):
        if self.texts[0] in self.icache:
            self.image, self.rect = self.icache[self.texts[0]]
        else:
            Effect.render(self)
            self.icache[self.texts[0]] = self.image, self.rect
    def update(self, text):
        self.texts[0] = text
        self.render()

class LevelNameEffect(CachedEffect):
    fontsize0 = 28
    fontname0 = "Merkin"
    def position(self, surf):
        self.rect.centerx = surf.get_rect().centerx
        self.rect.top = surf.get_rect().top + 2

class UpgradeTitle(Effect):
    fontsize0 = 50
    fontname0 = "Quigley"
    expiring = False
    color0 = 255,255,255
    color1 = 0,0,0
    def position(self, surf):
        self.rect.topleft = 6, 6

class PressSpaceEffect(Effect):
    fontsize0 = 40
    fontname0 = "Quigley"
    expiring = False
    color0 = 255,255,255
    color1 = 0,0,0
    def position(self, surf):
        self.rect.centerx = surf.get_rect().centerx
        self.rect.bottom = surf.get_rect().bottom - 20

class ActionIndicator(Effect):
    fontsize0 = 35
    def position(self, surf):
        x, y = surf.get_rect().bottomleft
        self.rect.bottomleft = x + 10, y - 10

class HeightIndicator(CachedEffect):
    def __init__(self):
        CachedEffect.__init__(self, "0ft")
    def update(self, h):
        CachedEffect.update(self, "%dft" % int(h))
    def position(self, surf):
        self.rect.left = 20
        self.rect.bottom = surf.get_height() - 10

class ProgressIndicator(CachedEffect):
    fontname0 = "freesansbold"
    fontsize0 = 38
    def __init__(self, goal):
        CachedEffect.__init__(self, "LLL0/%s" % goal)
        self.goal = goal
    def update(self, val):
        CachedEffect.update(self, "LLL%s/%s" % (val, self.goal))
    def position(self, surf):
        self.rect.right = surf.get_width() - 12
        self.rect.bottom = surf.get_height() - 10

class BonusIndicator(Effect):
    fontsize0 = 28
    fontname0 = "freesansbold"
    expiring = True
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self, hb):
        noise.play("cha-ching")
        Effect.__init__(self, ["LLL%s" % hb])

class CostIndicator(Effect):
    fontsize0 = 22
    fontname0 = "freesansbold"
    expiring = False
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self, cost, n = 0):
        Effect.__init__(self, ["LLL%s" % cost if cost else "maxed out"])
        self.n = n
    def update(self, cost):
        self.texts[0] = "LLL%s" % cost if cost else "maxed out"
        self.render()
    def position(self, surf):
        self.rect.topleft = 460, 72 + 32 * self.n

class HighScoreEffect(CachedEffect):
    fontsize0 = 22
    fontname0 = "freesansbold"
    def position(self, surf):
        self.rect.top = 90
        self.rect.centerx = surf.get_rect().centerx

class HCRecord(Effect):
    expiring = False
    fontsize0 = 36
    fontname0 = "KoolBean"
    color0 = 128, 128, 255
    color1 = 0, 0, 0
    def position(self, surf):
        self.rect.bottom = surf.get_rect().bottom - 20
        self.rect.right = surf.get_rect().right - 20

class BankIndicator(CostIndicator):
    fontsize0 = 40
    def __init__(self, bank, n = 0):
        Effect.__init__(self, ["LLL%s" % bank])
        self.n = n
    def update(self, bank):
        self.texts[0] = "LLL%s" % bank
        self.render()
    def position(self, surf):
        self.rect.top = surf.get_rect().top + 10
        self.rect.right = surf.get_rect().right - 10


class HeightBonusIndicator(BonusIndicator):
    def position(self, surf):
        self.rect.left = 20
        self.rect.bottom = surf.get_height() - 50 - int(self.age * 10)

class ComboIndicator(CachedEffect):
    fontname0 = "KoolBean"
    fontsize0 = 48
    color0 = 255, 32, 32
    color1 = 0, 0, 0
    def __init__(self):
        CachedEffect.__init__(self, "")
    def update(self, c):
        text = "%sxCOMBO" % c if c >= 2 else ""
        if text != self.texts[0]: self.age = 0
        CachedEffect.update(self, text)
    def position(self, surf):
        self.rect.left = 200
        self.rect.bottom = surf.get_height() - (12 if self.age < 0.1 else 2)

class ComboBonusIndicator(BonusIndicator):
    def position(self, surf):
        self.rect.left = 280
        self.rect.bottom = surf.get_height() - 50 - int(self.age * 10)

class NabBonusIndicator(BonusIndicator):
    def __init__(self, amt, pos):
        (x0, y0) = pos
        BonusIndicator.__init__(self, amt)
        self.x0, self.y0 = x0, y0
    def draw(self, surf):
        if not self.texts: return
        dx, dy = self.image.get_size()
        vista.blit(self.image, (self.x0 - dx/2, self.y0 + int(self.age*10)))

class CountdownIndicator(CachedEffect):
    fontname0 = "KoolBean"
    fontsize0 = 48
    color0 = 32, 255, 32
    color1 = 0, 0, 0
    def __init__(self, start):
        self.timeleft = start
        CachedEffect.__init__(self, "time:" + str(start))
    def think(self, dt):
        CachedEffect.think(self, dt)
        self.timeleft -= dt
        if self.timeleft < 10:
            self.color0 = 255, 32, 32
        if self.timeleft < 0:
            self.texts = []
        else:
            CachedEffect.update(self, "time:" + str(int(self.timeleft)))
    def position(self, surf):
        self.rect.bottom = surf.get_height() - 2
        self.rect.centerx = surf.get_rect().centerx + 140


class FeatIndicator(Effect):
    fontsize0 = 28
    fontname0 = "SFArchRival"
    expiring = False
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self, featname, n):
        self.n = n
        Effect.__init__(self, [featname])
    def position(self, surf):
        self.rect.topright = 102, 2 + 32 * self.n

class ContinueIndicator(Effect):
    fontsize0 = 28
    fontname0 = "SFArchRival"
    expiring = False
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self):
        Effect.__init__(self, ["continue"])
    def position(self, surf):
        self.rect.topleft = 172, 306


