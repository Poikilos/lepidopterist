import pygame
from pygame.locals import *
import data

def main():

    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("The Lepidopterist")
    pygame.mouse.set_visible(0)

    frames = {}
    frames["stand"] = pygame.image.load(data.filepath("you-stand.png")).convert_alpha()
    frames["run0"] = pygame.image.load(data.filepath("you-run-0.png")).convert_alpha()
    frames["run1"] = pygame.image.load(data.filepath("you-run-1.png")).convert_alpha()
    frames["run2"] = pygame.image.load(data.filepath("you-run-2.png")).convert_alpha()
    frames["nab0"] = pygame.image.load(data.filepath("you-nab-0.png")).convert_alpha()
    frames["nab1"] = pygame.image.load(data.filepath("you-nab-1.png")).convert_alpha()
    for k in frames.keys():
        frames[k + "-b"] = pygame.transform.flip(frames[k], True, False)

    clock = pygame.time.Clock()
    facingright = True
    x, y = 200, 100
    xmin, xmax = -50, 680
    nabbing = 0
    runtick = 0
    while True:
        dt = clock.tick(60) * 0.001

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                nabbing = 0.2
        k = pygame.key.get_pressed()
        dx = 0
        v = 300.
        if k[K_RIGHT]:
            dx += v * dt
        if k[K_LEFT]:
            dx -= v * dt

        xoff, yoff = 0, 0
        if nabbing:
            nabbing = max(nabbing - dt, 0)
            dx = 0
            picname = "nab1" if nabbing < 0.1 else "nab0"
        else:
            if dx:
                picname = ("run0", "run1", "run2", "run1")[int(4 * runtick / 0.5)]
                if "run" in picname: yoff = 10
                runtick += dt
                runtick %= 0.5
            else:
                picname = "stand"
                runtick = 0
        if dx:
            facingright = dx > 0
        x += dx
        x = max(min(x, xmax), xmin)

        if not facingright: picname = picname + "-b"
        
        screen.fill((192, 192, 255))
        screen.blit(frames[picname], (x + xoff, y + yoff))
        pygame.display.flip()

