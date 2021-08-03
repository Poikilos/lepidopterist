#!/usr/bin/env python3
'''
Manage settings.
'''
import sys
import os
import platform


enable_easy_shortcut = False  # use from other modules via easy_locked()


def easy_locked():
    return not enable_easy_shortcut


resolution = 800, 400
showdots = "--showdots" in sys.argv
printfps = "--printfps" in sys.argv
nosound = "--nosound" in sys.argv
nomusic = "--nomusic" in sys.argv
restart = "--restart" in sys.argv
cheat = "--cheat" in sys.argv
unlockall = "--unlockall" in sys.argv
alwaysshow = "--alwaysshow" in sys.argv  # Repeat cutscenes
hidefeatnames = "--hidefeatnames" in sys.argv
fullscreen = "--fullscreen" in sys.argv
easy = "--easy" in sys.argv
startInShop = "--start-shop" in sys.argv  # for testing
startInWorldMap = "--start-worldmap" in sys.argv  # for testing
visualDebug = "--visual-debug" in sys.argv  # for testing
verbose = "--verbose" in sys.argv

if not enable_easy_shortcut:
    easy = False


profile = None
if platform.system() == "Windows":
    profile = os.environ.get("USERPROFILE")
else:
    profile = os.environ.get("HOME")

picturesPath = None
if profile is not None:
    tryPictures = os.path.join(profile, "Pictures")
    if os.path.isdir(tryPictures):
        picturesPath = tryPictures
        if verbose:
            print('detected Pictures="{}"'.format(picturesPath))
    else:
        picturesPath = profile
        if verbose:
            print('There is no "{}" so Pictures="{}"'
                  ''.format(tryPictures, picturesPath))
else:
    if verbose:
        print('There is no profile so Pictures="{}"'
              ''.format(picturesPath))

screenshotsPath = picturesPath
if picturesPath is not None:
    tryScreenshots = os.path.join(picturesPath, "Screenshots")
    if os.path.isdir(tryScreenshots):
        screenshotsPath = tryScreenshots
        if verbose:
            print('detected Screenshots="{}"'.format(picturesPath))
    else:
        screenshotsPath = picturesPath
        if verbose:
            print('There is no "{}" so Screenshots="{}"'
                  ''.format(tryScreenshots, screenshotsPath))
else:
    if verbose:
        print('There is no ~/Pictures/Screenshots nor profile'
              ' so Screenshots="{}"'
              ''.format(screenshotsPath))


screenshotName = "screenshot-lepidopterist.png"
screenshotPath = screenshotName
if screenshotsPath is not None:
    screenshotPath = os.path.join(screenshotsPath, screenshotName)

print("screenshotPath: {}".format(screenshotPath))



savefile = "savegame"
for arg in sys.argv:
    if arg.startswith("--savefile="):
        savefile = arg[11:]

money0 = 0
for arg in sys.argv:
    if arg.startswith("--money="):
        money0 = int(arg[8:])



