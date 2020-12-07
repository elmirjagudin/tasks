#!/usr/bin/env python

from tasks_queue import CommandsQueue

cmd_queue = CommandsQueue()

while True:
    x = cmd_queue.dequeue_cmd()
    print(x)
