#!/usr/bin/env python

from sys import argv
from subprocess import Popen
import signal


def run_leaf():
    while True:
        signal.pause()


def run_node(level):
    Popen([argv[0], str(level)])
    Popen([argv[0], str(level)])
    signal.pause()


def main():
    if len(argv) != 2:
        print("need a level")
        return

    level = int(argv[1])
    if level == 0:
        run_leaf()
        return

    run_node(level - 1)


main()
