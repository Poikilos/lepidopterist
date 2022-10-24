#!/usr/bin/env python3
'''
Define the game world model and the screen.
'''

import pygame
import os
from pygame import *
from . import data
from . import settings
from . import loadlevel
import sys

sx0, sy0 = None, None
backdrops = {}


def init():
    global screen, sx, sy
    sx, sy = settings.resolution
    flags = pygame.FULLSCREEN if settings.fullscreen else 0
    screen = pygame.display.set_mode((sx, sy), flags)
    pygame.display.set_caption("Mortimer the Lepidopterist")
    pygame.mouse.set_visible(not settings.fullscreen)


def makegrass(level):
    global backdrops, backdrop
    if level in backdrops:
        backdrop = backdrops[level]
        return
    backdropfile = data.filepath("backdrop-%s.png" % level)
    backdrop = None
    image0 = None
    image1 = None
    bcolor = None
    if os.path.exists(backdropfile):
        backdrop = backdrops[level] = pygame.image.load(backdropfile).convert_alpha()
        return
    if level == 1:
        image0 = pygame.image.load(data.filepath("grassdead0001.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0194.jpg")).convert_alpha()
        bcolor = 80, 80, 80
    elif level == 2:
        image0 = pygame.image.load(data.filepath("brickmessy0009.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0220.jpg")).convert_alpha()
        bcolor = 128, 128, 128
    elif level == 3:
        image0 = pygame.image.load(data.filepath("grasstall0012.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0194.jpg")).convert_alpha()
        bcolor = 128, 128, 168
    elif level == 4:
        image0 = pygame.image.load(data.filepath("groundfrozen0014.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0188.jpg")).convert_alpha()
        bcolor = 30, 30, 60
    elif level == 5:
        image0 = pygame.image.load(data.filepath("waterplants0012.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0220.jpg")).convert_alpha()
        bcolor = 64, 64, 64
    elif level == 6:
        image0 = pygame.image.load(data.filepath("grasstall0012.jpg")).convert_alpha()
        image1 = pygame.image.load(data.filepath("skies0188.jpg")).convert_alpha()
        bcolor = 192, 92, 128
    else:
        image0 = pygame.image.load(level).convert_alpha()
        bcolor = 0, 0, 0
    w0, h0 = image0.get_size()
    yf0 = int(h0/2)
    w1 = None
    h1 = None
    enable_test = False
    if image1 is None:
        # This must be a test mode.
        print("Warning: image1 is not present,"
              " so the size of image0 will be used.")
        image1 = image0
        enable_test = True
    w1, h1 = image1.get_size()
    yf1 = int(150 * h1 / (vy1-vy0-300))

    try:
        array0 = pygame.surfarray.pixels_alpha(image0)
        array1 = pygame.surfarray.pixels_alpha(image1)
        for y in range(yf0):
            array0[:,y] = int(255*y/yf0)
        for y in range(yf1):
            array1[:,h1-y-1] = int(255*y/yf1)
        del array0, array1
    except ImportError:  # No surfarray
        for x in range(w0):
            for y in range(yf0):
                r,g,b,a = image0.get_at((x,y))
                image0.set_at((x,y), (r,g,b,int(255*y/yf0)))
        for x in range(w1):
            for y in range(yf1):
                r,g,b,a = image1.get_at((x,h1-y-1))
                image1.set_at((x,h1-y-1), (r,g,b,int(255*y/yf1)))

    grass = pygame.transform.scale(image0, (vx1-vx0,200))
    sky = pygame.transform.scale(image1, (vx1-vx0,(vy1-vy0-300)))

    backdrop = pygame.Surface((vx1-vx0,vy1-vy0)).convert_alpha()
    backdrop.fill(bcolor)
    backdrop.blit(sky,(0,0))
    backdrop.blit(grass,(0,vy1-vy0-200))
    backdrops[level] = backdrop
    if not enable_test:
        pygame.image.save(backdrop, backdropfile)


def levelinit(level):
    global vx0, vx1, vy0, vy1
    vx0, vx1, vy0, vy1 = loadlevel.getbox(level)
    makegrass(level)


def mapinit():
    global vx0, vx1, vy0, vy1, sx0, sy0
    vx0, vx1, vy0, vy1, sx0, sy0 = 0, sx, 0, sy, 0, 0


def constrain(x, y, rx = 0, ry = 0):
    x = max(min(x, vx1 - rx), vx0 + rx)
    y = max(min(y, vy1 - ry), vy0 + ry)
    return x, y


def position(pos, facingright, vy):
    (x,y) = pos
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


def mapclear():
    screen.fill((0, 0, 128))


def clear():
    # screen.fill((0, 128, 0), pygame.Rect(0, sy - (40 - sy0), 9999, 9999))
    screen.blit(backdrop, (int(0 - sx0), int(sy - (vy1 - sy0))))


def blit(img, pos):
    (x, y) = pos
    screen.blit(img, (int(x - sx0), int(sy - (y - sy0))))


def get_screen_pos(pos):
    (x, y) = pos
    return (int(x - sx0), int(sy - (y - sy0)))


def get_frame_screen_rect(frame, pos, width=None, height=None,
                          foot_ratio=.33):
    '''
    Sequential arguments:
    frame -- a sprite.Frame object
    pos -- a new center for the object
    Keyword arguments:
    foot_ratio -- Set how much of the bottom of the image is the feet.
                  The rect will be higher (inverse cartesian) by this
                  number times the height.
    width -- A new width for the rect,
             or None for the frame.image.get_rect().width
    height -- A new height for the rect,
              or None for the frame.image.get_rect().height
    '''
    result_rect = frame.image.get_rect().move(
        pos[0],
        pos[1],
    )
    pcPos = get_screen_pos(pos)
    if width is not None:
        result_rect.width = width
    result_rect.center = pcPos
    result_rect.top -= result_rect.height * foot_ratio
    return result_rect


def dot(pos):
    (x, y) = pos
    pygame.draw.circle(screen, (255, 128, 0), (int(x - sx0), int(sy - (y - sy0))), 4)


def line(pos1, pos2, color0=(255, 255, 255), color1=(0,0,0)):
    (x0, y0) = pos1
    (x1, y1) = pos2
    p0 = (int(x0 - sx0), int(sy - (y0 - sy0)))
    p1 = (int(x1 - sx0), int(sy - (y1 - sy0)))
    pygame.draw.line(screen, color0, p0, p1, 8)
    pygame.draw.line(screen, color1, p0, p1, 4)


def circle(pos, r, color=(255,128,0)):
    (x, y) = pos
    pygame.draw.circle(screen, color, (int(x - sx0), int(sy - (y - sy0))), int(r), 1)


if __name__ == "__main__":
    # Go to a module test mode if the module runs directly.
    pygame.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if len(joysticks) > 0:
        for joystick in joysticks:
            joystick.init()
    init()
    global vx0, vx1, vy0, vy1
    vx0, vx1, vy0, vy1 = loadlevel.getbox(1)
    position((200,100), True, 0)
    import os
    # dev_data = "dev-data"
    dev_data = data.get_data_dir()
    for sub in sorted(os.listdir(dev_data)):
        if not sub.endswith("jpg"):
            continue
        makegrass(os.path.join(dev_data, sub))
        clear()
        pygame.display.flip()
        while True:
            es = pygame.event.get()
            if any(e.type in (KEYDOWN, MOUSEBUTTONDOWN) for e in es):
                break
            if any(e.type in (JOYBUTTONDOWN, ) for e in es):
                break
            if any(e.type == QUIT for e in es):
                sys.exit()




