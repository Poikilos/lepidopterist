#!/usr/bin/env python3
'''
Manage persistent data.
'''
import pickle
import os
import data
import feat
import record
import settings


def save():
    state = feat.known, record.getstate()
    savefile = open(data.basepath("%s.pkl" % settings.savefile), "wb")
    pickle.dump(state, savefile)


def load():
    filename = data.basepath("%s.pkl" % settings.savefile)
    if not os.path.exists(filename):
        return
    savefile = open(filename, "rb")
    feat.known, recordstate = pickle.load(savefile)
    record.setstate(recordstate)


def remove():
    filename = data.basepath("%s.pkl" % settings.savefile)
    if os.path.exists(filename):
        os.remove(filename)


if not settings.restart:
    load()

