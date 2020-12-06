#!/usr/bin/env python

from sys import stderr
from time import sleep
from random import random

SLEEP_RANGE = 2

LOREM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu 
fugiat nulla pariatur. Excepteur  sint occaecat cupidatat non proident, sunt in 
culpa qui officia deserunt mollit anim id est laborum. 
"""


def spew_lorem():
    for line in LOREM.splitlines():
        print(line, flush=True)
        sleep_time = random() * SLEEP_RANGE
        stderr.write(f"sleeping for {sleep_time} secs\n")
        stderr.flush()

        sleep(sleep_time)


spew_lorem()
