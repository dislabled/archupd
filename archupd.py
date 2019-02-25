#!/usr/bin/python3

#
# "THE BEER-WARE LICENSE" (Revision 42)
#
# <dislabled@gmail.com> wrote these files. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
#
# TODO:
# * fix script
# * args so script will run checkupdates (file with last datetime?)

import re
import os
import sys
import itertools
import datetime as dt
import subprocess as sp
import feedparser


pacfile = '/home/stian/.config/polybar/scripts/archpkg/pac.txt'
aurfile = '/home/stian/.config/polybar/scripts/archpkg/aur.txt'
logfile = '/var/log/pacman.log'


def getworkingdir():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def getfeed():
    fd = feedparser.parse('https://www.archlinux.org/feeds/news')
    feed = []
    for f in range(0, 1):
        feed = [fd.entries[f].published[5:-6]]
        dt.datetime.strptime(feed[0], "%d %b %Y %H:%M:%S")
    feed.append([fd.entries[f].title])
    return feed


def lastupdate(logfile):
    with open(logfile, "r") as f:
        log = f.readlines()
        for l in log:
            if "starting full system upgrade" in l:
                date = re.search(r'\[(.*?)\]', l).group(1)
                dt.datetime.strptime(date, '%Y-%m-%d %H:%M')
    return date


def fileNOTempty(fname):
    return os.path.getsize(fname) > 0


def clearfile(fname):
    open(fname, 'w').close()


def choice():
    msg = 'update? '
    choice_1 = input('{:5} (y/N)'.format(msg)).lower() == 'y'
    if choice_1:
        return True


def update():
    if fileNOTempty(pacfile):
        sp.run('/usr/bin/sudo pacman -Syu', shell=True)
        clearfile(pacfile)
    if fileNOTempty(aurfile):
        sp.run('aurman -Syu', shell=True)
        clearfile(aurfile)
    input('\x1b[6:30:42m' + 'Finished...' + '\x1b[0m')
    exit


with open(getworkingdir() + "/gfx/arch.ans", 'r') as f:
    ansi = f.readlines()
with open(getworkingdir() + '/gfx/chkbox.ans', 'r') as f:
    ansi2 = f.readlines()
with open(getworkingdir() + '/gfx/exclmar.ans', 'r') as f:
    ansi3 = f.readlines()


def format_pkgdata():
    pac, aur = [], []
    with open(pacfile, 'r') as f:
        for w in f.readlines():
            pac.append(w.split())

    with open(aurfile, "r") as f:
        for w in f.readlines():
            aur.append(w.split())

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
    formatted1 = []
    if os.path.getsize(pacfile) > 0:
        formatted.append(pactxt)
        formatted.extend(pac)
    if os.path.getsize(aurfile) > 0:
        formatted.append(aurtxt)
        formatted.extend(aur)
    for p in range(len(formatted)):
        formatted1.append('{:30.40}{:18.18}{:^10}{:18.35}'.format(formatted[p][0], formatted[p][1], formatted[p][2], formatted[p][3]))
    return formatted1


def ansilen(line):
    ansi_code_re = re.compile('\\x1b\[[0-9;]*[a-zA-Z]')
    length = 0
    codes = ansi_code_re.findall(line)
    for c in codes:
        if c[-1] == 'C':
            length += int(c[2:-1])

    content = ansi_code_re.split(line)
    for c in content:
        length += len(c)

    return length


def totprint(data):
    ansimax = max([ansilen(l) for l in ansi]) + 3
    test = re.compile('\\x1b\[[0-9;]*[m]')
    count = 0
    for a, p in itertools.zip_longest(ansi, range(len(data)), fillvalue='-'):
        a = a.rstrip('\n')

        if count == 0:
            b = a
        last_color = test.findall(b)[-1:]
        if last_color:
            a = str(last_color[0]) + a + '\x1b[0m'
        linelen = ansilen(a)
        print("{}{}{}".format(a, " " * (ansimax - linelen), data[p]), end='\n')

#        print("{}{}{:30.40}{:18.18}{:^10}{:18.35}".format(a, " " * (ansimax - linelen), data[p][0],
#                                                          data[p][1], data[p][2], data[p][3]), end='\n')
    b = a


def main():
    date1 = lastupdate(logfile)
    date2 = getfeed()[0]
    if fileNOTempty(pacfile) or fileNOTempty(aurfile) is True:
        if date1 < date2:
            # newsprint(getfeed())
            print('Printing news now')
            if choice():
                update()
            else:
                exit
        else:
            totprint(format_pkgdata())
            if choice():
                update()
            else:
                exit
    else:
        for x in range(len(ansi2)):
            print(ansi2[x], end='')
        input('\x1b[6;30;42m' + 'Nothing to do...' + '\x1b[0m')


main()
