# Controls the gameplay area and also the screen

import pygame
from pygame import *
import data, settings

xmin, xmax = 30, 770
ymin, ymax = 0, 200

sx0, sy0 = None, None
vx0, vx1 = 0, 1000
vy0, vy1 = -40, 1000

def init():
    global screen, grass, sx, sy
    sx, sy = settings.resolution
    screen = pygame.display.set_mode((sx, sy))
    pygame.display.set_caption("Mortimer the Lepidopterist")
#    pygame.mouse.set_visible(0)
    grass = pygame.image.load(data.filepath("grass.jpg"))


def constrain(x, y, rx = 0, ry = 0):
    x = max(min(x, vx1 - rx), vx0 + rx)
    y = max(min(y, vy1 - ry), vy0 + ry)
    return x, y

def position((x,y), facingright, vy):
    global gx, gy, sx0, sy0
    gx = x - sx/2 + (200 if facingright else -200)
    gy = y - sy/2 + 60
    if sx0 is None:
        sx0, sy0 = gx, gy

def think(dt):
    global sx0, sy0
    dx, dy = gx - sx0, gy - sy0
    sx0 = gx if abs(dx) < 400 * dt else sx0 + (400 if dx > 0 else -400) * dt
    sy0 = gy if abs(dy) < 400 * dt else sy0 + (400 if dy > 0 else -400) * dt
    if vx1 - vx0 <= sx:
        sx0 = (vx1 - vx0 - sx)/2
    else:
        sx0 = min(max(sx0, vx0), vx1 - sx)
    if vy1 - vy0 <= sy:
        sy0 = (vy1 - vy0 - sy)/2
    else:
        sy0 = min(max(sy0, vy0), vy1 - sy)

def clear():
    screen.fill((192, 192, 255))
#    screen.fill((0, 128, 0), pygame.Rect(0, sy - (40 - sy0), 9999, 9999))
    screen.blit(grass, (int(0 - sx0), int(sy - (250 - sy0))))

def blit(img, (x, y)):
    screen.blit(img, (int(x - sx0), int(sy - (y - sy0))))

def dot((x, y)):
    pygame.draw.circle(screen, (255, 128, 0), (int(x - sx0), int(sy - (y - sy0))), 4)

def circle((x, y), r):
    pygame.draw.circle(screen, (255, 128, 0), (int(x - sx0), int(sy - (y - sy0))), int(r), 1)

