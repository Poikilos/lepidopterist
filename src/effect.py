# Graphic text effects

import pygame
from pygame.locals import *
import data

fontcache = {}

class Effect(object):
    fontsize0 = 120
    fontname0 = "fightingspirit"
    expiring = True
    color0 = 255, 128, 0
    color1 = 255, 255, 0
    bratio = 32
    
    def __init__(self, texts, fontsize = None, fontname = None):
        if fontsize is None: fontsize = self.fontsize0
        if fontname is None: fontname = self.fontname0
        self.fontsize = fontsize
        self.fontname = fontname
        key = self.fontname, self.fontsize
        if key not in fontcache:
            fontcache[key] = pygame.font.Font(data.filepath("%s.ttf" % self.fontname), self.fontsize)
        self.font = fontcache[key]
        self.texts = texts
        self.render()
    def render(self):
        self.image0 = self.font.render(self.texts[0], True, self.color0)
        self.image1 = self.font.render(self.texts[0], True, self.color1)
        d = self.fontsize / self.bratio
        self.image = pygame.Surface((self.image0.get_width() + 2*d, self.image0.get_height() + 2*d)).convert_alpha()
        self.image.fill((0,0,0,0))
        self.image.blit(self.image1, (0,0))
        self.image.blit(self.image1, (0,2*d))
        self.image.blit(self.image1, (2*d,0))
        self.image.blit(self.image1, (2*d,2*d))
        self.image.blit(self.image0, (d,d))
        self.rect = self.image.get_rect()
        self.age = 0
    def think(self, dt):
        if not self.texts: return
        if not self.expiring: return
        self.age += dt
        if self.age > 0.5 + 0.05 * len(self.texts[0]):
            self.age -= 0.5 + 0.05 * len(self.texts[0])
            del self.texts[0]
            if self.texts: self.render()
    def position(self, surf):
        self.rect.center = surf.get_rect().center
    def draw(self, surf):
        if not self.texts: return
        self.position(surf)
        surf.blit(self.image, self.rect)
    def __nonzero__(self):
        return bool(self.texts)

class ActionIndicator(Effect):
    fontsize0 = 35
    def position(self, surf):
        x, y = surf.get_rect().bottomleft
        self.rect.bottomleft = x + 10, y - 10

class FeatIndicator(Effect):
    fontsize0 = 26
    fontname0 = "Anonymous"
    expiring = False
    color0 = 255, 255, 255
    color1 = 0, 0, 0
    bratio = 18
    def __init__(self, featname, n):
        self.n = n
        Effect.__init__(self, [featname])
    def position(self, surf):
        self.rect.topright = 100, 10 + 32 * self.n



