#!/usr/bin/python3

#
# "THE BEER-WARE LICENSE" (Revision 42)
#
# <dislabled@gmail.com> wrote these files. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.
#
# TODO:
# * only clear files after successful update
# * args so script will run checkupdates (file with last datetime?)

import re
import os
import sys
import pytz
import itertools
import datetime as dt
import subprocess as sp
import feedparser

paclist = sp.check_output('checkupdates').decode('UTF-8')
aurlist = sp.check_output('checkupdates-aur').decode('UTF-8')
logfile = '/var/log/pacman.log'
ipac = ['linux', 'systemd', 'glibc', 'gcc', 'gcc-libs', 'cmake', 'pacman']


def getworkingdir():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def getfeed():
    fd = feedparser.parse('https://www.archlinux.org/feeds/news')
    feed = []
    for f in range(0, 1):
        feed = [fd.entries[f].published[5:-6]]
    feed.append([fd.entries[f].title])
    return feed


def lastupdate(logfile):
    with open(logfile, "r") as f:
        log = f.readlines()
        for l in log:
            if "starting full system upgrade" in l:
                date = re.search(r'\[(.*?)\]', l).group(1)
    return date


def clearfile(fname):
    open(fname, 'w').close()


def choice(msg):
    choice_1 = input('{:5} (y/N)'.format(msg)).lower() == 'y'
    if choice_1:
        return True


def update():
    if paclist or aurlist:
        sp.run('pikaur -Syu', shell=True)
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
    for w in paclist.splitlines():
        pac.append(w.split())
    for w in aurlist.splitlines():
        aur.append(w.split())
    pactxt = [("\x1b[1;34mPac:"),
              ("------------------"), ("--"), ("-----------\x1b[0m")]
    aurtxt = [("\x1b[1;34mAur:"),
              ("------------------"), ("--"), ("-----------\x1b[0m")]
    d = []
    dret = []
    if paclist:
        d.append(pactxt)
        d.extend(pac)
    if aurlist:
        d.append(aurtxt)
        d.extend(aur)
    for p in range(len(d)):
        if any(sw in d[p][0] for sw in ipac):
            d[p][0] = '\x1b[31m' + d[p][0] + '\x1b[0m'
        dret.append('{:.27}{}{:18.18}{:^10}{:18.18}'.format(d[p][0], " " * (30 - min(ansilen(d[p][0]), 27)),
                                                            d[p][1], d[p][2], d[p][3]))
    return dret


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
    for a, p in itertools.zip_longest(ansi, data, fillvalue=''):
        a = a.rstrip('\n')

        if count == 0:
            b = a
        last_color = test.findall(b)[-1:]
        if last_color:
            a = str(last_color[0]) + a + '\x1b[0m'
        linelen = ansilen(a)
        print("{}{}{}".format(a, " " * (ansimax - linelen), p), end='\n')
    b = a


def main():
    try:
        date1 = dt.datetime.strptime(lastupdate(logfile), '%Y-%m-%d %H:%M')
    except ValueError:
        date1 = dt.datetime.strptime(lastupdate(logfile), '%Y-%m-%dT%H:%M:%S%z')
    date2 = dt.datetime.strptime(getfeed()[0], '%d %b %Y %H:%M:%S')
    if paclist or aurlist !=  None:
        if date1 < pytz.utc.localize(date2):
            totprint(getfeed())
            if choice("continue showing packages? "):
                sp.call('clear')
                totprint(format_pkgdata())
                if choice("update? "):
                    update()
                else:
                    exit
            else:
                exit
        else:
            totprint(format_pkgdata())
            if choice("update? "):
                update()
            else:
                exit
    else:
        for x in range(len(ansi2)):
            print(ansi2[x], end='')
        input('\x1b[6;30;42m' + 'Nothing to do...' + '\x1b[0m')


main()
