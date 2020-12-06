#!/usr/bin/env python

import asyncio
from pathlib import Path
from sys import stdin
from itertools import count
from threading import Thread


async def log_output(stream, log_file):
    print(f"log {stream} to {log_file}")

    with log_file.open("wb") as log:
        while True:
            buf = await stream.read(1024 * 4)
            if not buf:
                break

            log.write(buf)
            log.flush()


async def run_command(command, stdout_log, stderr_log):
    print(f"running '{command}'")

    try:
        proc = await asyncio.create_subprocess_exec(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await asyncio.gather(
            log_output(proc.stdout, stdout_log), log_output(proc.stderr, stderr_log)
        )

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
    LOGS_DIR = Path("logs")

    def __init__(self, loop):
        self.loop = loop
        self.tasks = {}
        self.task_ids = count(1)

    def start_task(self, command):
        def _log_paths():
            return (
                Path(self.LOGS_DIR, f"stdout-{task_id}.log"),
                Path(self.LOGS_DIR, f"stderr-{task_id}.log"),
            )

        task_id = self.task_ids.__next__()

        task_future = asyncio.run_coroutine_threadsafe(
            run_command(command, *_log_paths()), self.loop
        )

        self.tasks[task_id] = task_future
        return task_id

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
