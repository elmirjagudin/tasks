#!/usr/bin/env python

import asyncio
from sys import stdin
from itertools import count
from threading import Thread


async def read_stdout(stdout):
    print("read_stdout")
    while True:
        buf = await stdout.read(1024 * 4)
        if not buf:
            break

        print(f"stdout: { buf }")


async def read_stderr(stderr):
    print("read_stderr")
    while True:
        buf = await stderr.read()
        if not buf:
            break

        print(f"stderr: { buf }")


async def run_command(command):
    print(f"running '{command}'")

    try:
        proc = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await asyncio.gather(read_stderr(proc.stderr), read_stdout(proc.stdout))

    #        stdout, stderr = await proc.communicate()

    # print(f"[{command!r} exited with {proc.returncode}]")
    # if stdout:
    #     print(f"[stdout]\n{stdout.decode()}")
    # if stderr:
    #     print(f"[stderr]\n{stderr.decode()}")
    except asyncio.CancelledError:
        print("i'm canceled, terminating command")
        proc.terminate()
        raise

    print(f"DONE running '{command}'")


def parse_command(line):
    command, args = line.strip().split(maxsplit=1)
    return command, args.strip()


def start_loop():
    def _runner():
        asyncio.set_event_loop(loop)
        loop.run_forever()
        print("loop stopped")

    loop = asyncio.new_event_loop()
    th = Thread(target=_runner)
    th.start()

    return loop, th


def stop_loop(loop, loop_thread):
    loop.call_soon_threadsafe(loop.stop)
    loop_thread.join()


class Tasks:
    def __init__(self, loop):
        self.loop = loop
        self.tasks = {}
        self.task_ids = count(1)

    def start_task(self, command):
        task_future = asyncio.run_coroutine_threadsafe(run_command(command), self.loop)

        return self._add_task(task_future)

    def cancel_task(self, task_id):
        if task_id not in self.tasks:
            print(f"unknown task ID {task_id}")
            return

        task_future = self.tasks[task_id]
        if task_future.done():
            print("can cancel done task, tsk tsk")
            return

        task_future.cancel()

    def _add_task(self, task):
        task_id = self.task_ids.__next__()
        self.tasks[task_id] = task

        return task_id


def main():
    loop, loop_thread = start_loop()

    tasks = Tasks(loop)

    while (line := stdin.readline()) != "":
        command, args = parse_command(line)

        if command == "r":
            task_id = tasks.start_task(args)
            print(task_id)
        elif command == "c":
            tasks.cancel_task(int(args))
        else:
            print(f"unknown command '{command}'")

    stop_loop(loop, loop_thread)


main()
