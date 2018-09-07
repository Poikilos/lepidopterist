# This module is probably going to balloon out of control, but here goes.

import pygame, random, math
from pygame.locals import *
import data, vista, settings

frames = {}
class Frame(object):
    def __init__(self, filename, (dx, dy), hflip = False):
        self.filename = filename
        self.image = pygame.image.load(data.filepath(self.filename)).convert_alpha()
        if hflip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.dx, self.dy = dx, dy
        self.nabbed = False
    def draw(self, (x, y)):
        vista.blit(self.image, (x - self.dx, y + self.dy))
        if settings.showdots:
            vista.dot((x, y))
#        pygame.draw.circle(surf, (255, 128, 0, 255), (int(px), int(py)), 4)
    def reverse(self):
        return Frame(self.filename, (self.image.get_width() - self.dx, self.dy), True)

def load():
    frames["stand"] = Frame("you-stand.png", (94, 150))
    frames["run0"] = Frame("you-run-0.png", (84, 145))
    frames["run1"] = Frame("you-run-1.png", (84, 150))
    frames["run2"] = Frame("you-run-2.png", (84, 145))
    frames["nab0"] = Frame("you-nab-0.png", (94, 150))
    frames["nab1"] = Frame("you-nab-1.png", (94, 150))
    frames["twirl0"] = Frame("you-twirl-0.png", (94, 150))
    frames["twirl1"] = Frame("you-twirl-1.png", (94, 150))
    frames["blue0"] = Frame("blue-butterfly-0.png", (36, 36))
    frames["blue1"] = Frame("blue-butterfly-1.png", (36, 36))
    frames["red0"] = Frame("red-butterfly-0.png", (36, 36))
    frames["red1"] = Frame("red-butterfly-1.png", (36, 36))
    frames["yellow0"] = Frame("yellow-butterfly-0.png", (36, 36))
    frames["yellow1"] = Frame("yellow-butterfly-1.png", (36, 36))
    for k in frames.keys():
        frames[k + "-b"] = frames[k].reverse()


class Butterfly(object):
    fnames = ("blue0", "blue1")
    ymin, ymax = 60, 160
    def __init__(self, p = None, (vx, vy) = (250, 50)):
        if p == None:
            self.x = random.uniform(vista.vx0, vista.vx1)
            self.y = random.uniform(self.ymin, self.ymax)
        else:
            self.x, self.y = p
        self.vx, self.vy = vx, vy
        self.bangle = None
        self.flaptick = random.random()
    def think(self, dt):
        if random.uniform(0, 0.5) < dt or self.bangle is None:
            self.bangle = random.uniform(0, 6.28)
        self.dbx, self.dby = self.vx * dt * math.cos(self.bangle), self.vy * dt * math.sin(self.bangle)
        self.flaptick += dt
        self.x += self.dbx
        self.y += self.dby
        self.y = max(min(self.y, self.ymax), self.ymin)
        self.x, self.y = vista.constrain(self.x, self.y)
    def draw(self):
        bpicname = self.fnames[int(self.flaptick / 0.1) % 2]
        if self.dbx > 0: bpicname = bpicname + "-b"
        frames[bpicname].draw((self.x, self.y))

class YButterfly(Butterfly):
    fnames = ("yellow0", "yellow1")
    ymin, ymax = 160, 260

class RButterfly(Butterfly):
    fnames = ("red0", "red1")
    ymin, ymax = 260, 360


