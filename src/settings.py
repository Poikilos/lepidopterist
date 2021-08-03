#!/usr/bin/env python3
'''
Manage settings.
'''
import sys

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
if not enable_easy_shortcut:
    easy = False

savefile = "savegame"
for arg in sys.argv:
    if arg.startswith("--savefile="):
        savefile = arg[11:]

money0 = 0
for arg in sys.argv:
    if arg.startswith("--money="):
        money0 = int(arg[8:])



