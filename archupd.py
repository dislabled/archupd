#!/usr/bin/env python
#
# "THE BEER-WARE LICENSE" (Revision 42)
#
# <dislabled@gmail.com> wrote these files. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
#
# TODO:
# * get update message beside arch/messages logo
# * args so script will run checkupdates (file with last datetime?)


import subprocess as sp
import feedparser
import datetime
import re
import os
import itertools
import ansiwrap


pacfile = "/home/stian/Projects/testing/pac.txt"
aurfile = "/home/stian/Projects/testing/aur.txt"
fd = feedparser.parse("https://www.archlinux.org/feeds/news/")

def feed_get():
    feed = []
    for f in range(0, 1):
        feed = [fd.entries[f].published[5:-6]]
        datetime.datetime.strptime(feed[0], "%d %b %Y %H:%M:%S")
        feed.append([fd.entries[f].title])
        return feed


def lsudate(logfile):
    with open(logfile, "r") as f:
        log = f.readlines()
        for l in log:
            if "starting full system upgrade" in l:
                date = re.search(r'\[(.*?)\]', l).group(1)
                datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
    return date


def file_nempty(fname):
    return os.path.getsize(fname) > 0


def import_file(fname):
    data = []
    with open(fname) as f:
        for l in f.readlines():
            data.append(l.split())
        pass
    return data


def formatpkgdata():
    pac = import_file(pacfile)
    aur = import_file(aurfile)
    for x in range(len(aur)):
        try:
            aur[x].remove("::")
        except ValueError:
            pass
    pactxt = [("\x1b[1;34mPac:                          "),
              ("------------------"), ("--"), ("-----------\x1b[0m")]
    aurtxt = [("\x1b[1;34mAur:                          "),
              ("------------------"), ("--"), ("-----------\x1b[0m")]
    formatted = []
    if file_nempty(pacfile):
        formatted.append(pactxt)
        formatted.extend(pac)
    if file_nempty(aurfile):
        formatted.append(aurtxt)
        formatted.extend(aur)
    return formatted


def ansi(filename):
        localdir = '/home/stian/scripts/archupd/'
        filepath = os.path.join(localdir, filename)

        with open(filepath, "r") as f:
            ansivar = f.readlines()
        width = 0
        widtha = 0
        # get max width for this ansi
        for bz in range(len(ansivar)):
            if ansiwrap.ansilen(ansivar[bz]) >= widtha:
                widtha = ansiwrap.ansilen(ansivar[bz])
        for l1 in range(len(ansivar)):
            if len(ansivar[l1]) >= width:
                width = len(ansivar[l1])
        for line in range(len(ansivar)):
#            for z in range(width-ansiwrap.ansilen(ansivar[line])):
            for z in range(width-len(ansivar[line])):
                 ansivar[line] = ansivar[line].rstrip("\n") + "X"
#                 ansivar[line] = ansiwrap.strip_color(ansivar[line]).rstrip() + "X"
        print(widtha)
        print(width)
        return ansivar


def pacprint(data):
    archans = ansi("arch.ans")

    for x, y in itertools.zip_longest(range(len(data)), range(len(archans))):
        if x is None:
            # format only ansi
            print('{:_<50.99}'.format(archans[y]))
        elif y is None:
            # format after ansi ran out
            print('{:50.50} {:30.40} {:18.18} {:^10} {:18.35}'.format(
                        "", data[x][0], data[x][1], data[x][2], data[x][3]))
        else:
            # format with both ansi and text
            print('{:50.200} {:30.40} {:18.18} {:^10} {:18.35}'.format(
                    archans[y], data[x][0], data[x][1], data[x][2], data[x][3]))


def newsprint(data):
    archans = ansi("arch.ans")

    for x, y in itertools.zip_longest(range(1), range(len(archans))):
        if y is not None:
            for z in range(50-ansiwrap.ansilen(archans[y])):
                archans[y] = archans[y] + " "
        if x is None:
            print('{:50.99}'.format(archans[y]))
        else:
            print('{:50.99} {:16.16} {:60.60}'.format(
                    archans[y], data[0], data[1][x]))


def choice():
    msg = 'update? '
    choice_1 = input("{:5} (y/N)".format(msg)).lower() == 'y'
    if choice_1:
        return True


def update():
    if file_nempty(pacfile):
        sp.run("/usr/bin/sudo pacman -Syu", shell=True)
        clear_file(pacfile)
    if file_nempty(aurfile):
        sp.run("aurman -Syu", shell=True)
        clear_file(aurfile)
    input("\x1b[6;30;42m" + "Finished..." + "\x1b[0m")
    exit


pacprint(formatpkgdata())
