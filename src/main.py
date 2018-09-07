import pygame, math, random
from pygame.locals import *
import data

frames = {}
class Frame(object):
    def __init__(self, filename, (dx, dy), hflip = False):
        self.filename = filename
        self.image = pygame.image.load(data.filepath(self.filename)).convert_alpha()
        if hflip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.dx, self.dy = dx, dy
        self.nabbed = False
    def draw(self, surf, (px, py)):
        surf.blit(self.image, (px - self.dx, py - self.dy))
#        pygame.draw.circle(surf, (255, 128, 0, 255), (int(px), int(py)), 4)
    def reverse(self):
        return Frame(self.filename, (self.image.get_width() - self.dx, self.dy), True)

class Butterfly(object):
    def __init__(self, (x, y), (vx, vy) = (250, 50)):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.bangle = None
        self.flaptick = random.random()
    def think(self, dt):
        if random.uniform(0, 0.5) < dt or self.bangle is None:
            self.bangle = random.uniform(0, 6.28)
        self.dbx, self.dby = 250 * dt * math.cos(self.bangle), 50 * dt * math.sin(self.bangle)
        self.flaptick += dt
        self.x = max(min(self.x + self.dbx, xmax), xmin)
        self.y = max(min(self.y + self.dby, ymax), ymin)
    def draw(self, surf):
        bpicname = ("blue0", "blue1")[int(self.flaptick / 0.1) % 2]
        if self.dbx > 0: bpicname = bpicname + "-b"
        frames[bpicname].draw(surf, (self.x, self.y))
        

class Effect(object):
    fonts = {}
    def __init__(self, texts, fontsize = 120):
        self.fontsize = fontsize
        self.fontname = "fightingspirit"
        key = self.fontname, self.fontsize
        if key not in self.fonts:
            self.fonts[key] = pygame.font.Font(data.filepath("%s.ttf" % self.fontname), self.fontsize)
        self.font = self.fonts[key]
        self.texts = texts
        self.render()
    def render(self):
        self.image0 = self.font.render(self.texts[0], True, (255, 128, 0))
        self.image1 = self.font.render(self.texts[0], True, (255, 255, 0))
        d = self.fontsize / 18
        self.image = pygame.Surface((self.image0.get_width() + d, self.image0.get_height() + d)).convert_alpha()
        self.image.fill((0,0,0,0))
        self.image.blit(self.image1, (d,d))
        self.image.blit(self.image0, (0,0))
        self.rect = self.image.get_rect()
        self.age = 0
    def think(self, dt):
        if not self.texts: return
        self.age += dt
        if self.age > 0.5 + 0.05 * len(self.texts[0]):
            self.age -= 0.5 + 0.05 * len(self.texts[0])
            del self.texts[0]
            if self.texts: self.render()
    def draw(self, surf):
        if not self.texts: return
        self.rect.center = surf.get_rect().center
        surf.blit(self.image, self.rect)
    def __nonzero__(self):
        return bool(self.texts)

xmin, xmax = 30, 770
ymin, ymax = 0, 200

def main():

    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("Mortimer the Lepidopterist")
    pygame.mouse.set_visible(0)

    frames["stand"] = Frame("you-stand.png", (94, 150))
    frames["run0"] = Frame("you-run-0.png", (84, 145))
    frames["run1"] = Frame("you-run-1.png", (84, 150))
    frames["run2"] = Frame("you-run-2.png", (84, 145))
    frames["nab0"] = Frame("you-nab-0.png", (94, 150))
    frames["nab1"] = Frame("you-nab-1.png", (94, 150))
    frames["blue0"] = Frame("blue-butterfly-0.png", (36, 36))
    frames["blue1"] = Frame("blue-butterfly-1.png", (36, 36))
    for k in frames.keys():
        frames[k + "-b"] = frames[k].reverse()

    butterflies = [Butterfly((random.uniform(xmin, xmax), random.uniform(ymin, ymax))) for j in range(6)]

    clock = pygame.time.Clock()
    facingright = True
    x, y = 200, 200
    nabbing = 0
    leaping = 0
    runtick = 0
    title = Effect(["READY", "SET", "COLLECT"])
    endtitle = Effect(["YOU WON", "BUT IN YOUR QUEST", "TO BECOME THE", "WORLD'S GREATEST", "LEPIDOPTERIST", "THE ONE THING", "YOU NEVER CAUGHT", "...", "WAS LOVE"], 60)
    while True:
        dt = clock.tick(60) * 0.001

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if not leaping and not nabbing:
                    nabbing = 0.2
            elif event.type == KEYDOWN and event.key == K_UP:
                if not leaping and not nabbing:
                    leaping = 0.5

        k = pygame.key.get_pressed()
        dx = 0
        v = 300.
        if k[K_RIGHT]:
            dx += v * dt
        if k[K_LEFT]:
            dx -= v * dt

        y = 200
        if nabbing:
            nabbing = max(nabbing - dt, 0)
            dx = 0
            picname = "nab1" if nabbing < 0.1 else "nab0"
            nx, ny = x + (40 if facingright else -40), y - 80
            for b in list(butterflies):
                adx, ady = b.x - nx, b.y - ny
                if adx ** 2 + ady ** 2 < 40 ** 2:
                    b.nabbed = True
                    butterflies.remove(b)
        elif leaping:
            leaping = max(leaping - dt, 0)
            picname = "run2"
            y = 200 - 400 * leaping * (0.5 - leaping)
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
        x = max(min(x + dx, xmax), xmin)
        if not facingright: picname = picname + "-b"
        
        for b in butterflies: b.think(dt)
        title.think(dt)
        if not butterflies:
            endtitle.think(dt)
        
        screen.fill((128, 128, 255))
        screen.fill((0, 128, 0), pygame.Rect(0, ymax - 40, 9999, 9999))
        frames[picname].draw(screen, (x, y))
        for b in butterflies: b.draw(screen)
#        if nabbing:
#            pygame.draw.circle(screen, (255, 128, 0), (nx, ny), 4)
        title.draw(screen)
        if not butterflies:
            endtitle.draw(screen)
        pygame.display.flip()
        if not endtitle:
            exit()

