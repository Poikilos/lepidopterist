import pygame, math, random
from pygame.locals import *
import data, combo, effect, vista, feat, sprite, settings


def main():

    pygame.init()
    vista.init()
    sprite.load()

    butterflies = [sprite.Butterfly() for j in range(6)]
    butterflies += [sprite.YButterfly() for j in range(6)]
    butterflies += [sprite.RButterfly() for j in range(6)]

    clock = pygame.time.Clock()
    facingright = True
    x, y, g, vy = 200, 0, 500, 0
    leapvx, leapvy = 200., 200.
    twirlvy = 300.
    nabvx = 400.
    runvx = 300.
    nabtick, nabtime = 0, 0.25
    nabradius = 50
    leaping = 0
    runtick = 0
    twirltick = 0
    currentfeat = ""
    grounded = True
    title = effect.Effect(["READY", "SET", "COLLECT"])
    endtitle = effect.Effect(["YOU WON", "BUT IN YOUR QUEST", "TO BECOME THE", "WORLD'S GREATEST", "LEPIDOPTERIST", "THE ONE THING", "YOU NEVER CAUGHT", "...", "WAS LOVE"], 60)
    atitle = None
    feat.startlevel()
    while True:
        dt = clock.tick(60) * 0.001
        if settings.printfps and random.random() < dt:
            print clock.get_fps()

        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                exit()
            elif event.type == KEYDOWN and event.key == K_F12:
                pygame.image.save(vista.screen, "screenshot.png")

        k = pygame.key.get_pressed()
        kcombo = combo.check(k)

        if grounded:
            dx = 0
            if k[K_RIGHT]:
                dx += runvx * dt
            if k[K_LEFT]:
                dx -= runvx * dt
            if nabtick:
                dx = 0
            if dx:
                facingright = dx > 0
                currentfeat = "run"
                x += dx
            elif not nabtick:
                currentfeat = ""

            if kcombo == "leap" and "leap" in feat.known:
                if feat.attempt("leap"):
                    vx = leapvx if facingright else -leapvx
                    vy = leapvy
                    grounded = False
                    currentfeat = "leap"
                    atitle = effect.ActionIndicator(["LEAP"])
            elif kcombo == "twirl" and "twirl" in feat.known:
                if feat.attempt("twirl"):
                    grounded = False
                    currentfeat = "twirl"
                    vx = 0
                    vy = twirlvy
                    atitle = effect.ActionIndicator(["TWIRL"])
                    twirltick = 1
            elif kcombo == "nab" and "nab" in feat.known:
                if feat.attempt("nab"):
                    currentfeat = "nab"
                    nabtick = nabtime
                    atitle = effect.ActionIndicator(["NAB"])
        else:
            if kcombo == "leap" and "leap" in feat.known:
                if feat.attempt("leap"):
                    vx = leapvx if facingright else -leapvx
                    vy = leapvy
                    atitle = effect.ActionIndicator(["LEAP"])
                    twirltick = 0
            elif kcombo == ("turn-r" if facingright else "turn-l") and "turn" in feat.known:
                if feat.attempt("turn"):
                    facingright = not facingright
                    vx = leapvx if facingright else -leapvx
                    vy = leapvy
                    atitle = effect.ActionIndicator(["TURN"])
                    twirltick = 0
            elif kcombo == "nab" and "nab" in feat.known:
                if feat.attempt("nab"):
                    currentfeat = "nab"
                    nabtick = nabtime
                    vx = nabvx if facingright else -nabvx
                    atitle = effect.ActionIndicator(["NAB"])
                    twirltick = 0
            elif kcombo == "twirl" and "twirl" in feat.known:
                if feat.attempt("twirl"):
                    currentfeat = "twirl"
                    vx = 0
                    vy = twirlvy
                    atitle = effect.ActionIndicator(["TWIRL"])
                    twirltick = 1

            if nabtick:
                pass
            elif twirltick:
                currentfeat = "twirl"
            else:
                currentfeat = "leap"

            if nabtick:
                x += vx * dt
            else:
                x += vx * dt
                y += vy * dt
                vy -= g * dt
            if y < 0:
                y = 0
                vy = 0
                grounded = True
                feat.land()
                currentfeat = ""
                twirltick = 0

        x, y = vista.constrain(x, y, 30)

        if nabtick:
            nabtick = max(nabtick - dt, 0)
            nx, ny = x + (40 if facingright else -40), y + 80
            for b in list(butterflies):
                adx, ady = b.x - nx, b.y - ny
                if adx ** 2 + ady ** 2 < nabradius ** 2:
                    b.nabbed = True
                    butterflies.remove(b)


        if currentfeat == "leap":
            picname = "run2"
        elif currentfeat == "run":
            picname = ("run0", "run1", "run2", "run1")[int(4 * runtick / 0.5)]
            runtick += dt
            runtick %= 0.5
        elif currentfeat == "nab":
            picname = "nab1" if nabtick < nabtime / 2. else "nab0"
        elif currentfeat == "twirl":
            twirltick += dt
            twirltick %= 0.3
            picname = ("twirl0", "twirl1-b", "twirl1", "twirl0-b")[int(4 * twirltick / 0.3)]
        else:
            picname = "stand"
        if "twirl" not in picname and not facingright:
            picname = picname + "-b"
        vista.position((x, y), facingright, vy)
        
        feat.think(dt)
        vista.think(dt)
        for b in butterflies: b.think(dt)
        title.think(dt)
        if atitle: atitle.think(dt)
        if not butterflies:
            endtitle.think(dt)
        
        vista.clear()
        sprite.frames[picname].draw((x, y))
        for b in butterflies:
            b.draw()
        if nabtick and settings.showdots:
            vista.circle((int(nx), int(ny)), nabradius)
        feat.draw()
        title.draw(vista.screen)
        if atitle: atitle.draw(vista.screen)
        if not butterflies:
            endtitle.draw(vista.screen)
        pygame.display.flip()
        if not endtitle:
            exit()

