from json import dumps, loads
from redis import Redis


class TaskCommand:
    def serialize(self):
        return dumps(self._as_dict())


class StartTask(TaskCommand):
    TYPE = "start_task"

    def __init__(self, binary, arguments):
        self.binary = binary
        self.arguments = arguments

    def _as_dict(self):
        return {
            "cmd": self.TYPE,
            "task": {
                "binary": self.binary,
                "arguments": self.arguments,
                "stdlog": "hej.log",
                "errlog": "err.log",
            },
        }

    @staticmethod
    def from_dict(json_dict):
        task = json_dict["task"]

        return StartTask(task["binary"], task["arguments"])

    def __str__(self):
        return f"StartTask: binary '{self.binary}' arguments {self.arguments}"


class CancelTask(TaskCommand):
    TYPE = "cancel_task"

    def __init__(self, task_id):
        self.task_id = task_id

    def _as_dict(self):
        return {
            "cmd": self.TYPE,
            "task_id": self.task_id,
        }

    @staticmethod
    def from_dict(json_dict):
        return CancelTask(json_dict["task_id"])

    def __str__(self):
        return f"CancelTask: task_id '{self.task_id}'"


def _deserialize_command(data):
    json_dict = loads(data.decode())

    cmd = json_dict["cmd"]
    if cmd == "start_task":
        return StartTask.from_dict(json_dict)

    if cmd == "cancel_task":
        return CancelTask.from_dict(json_dict)

    raise ValueError(f"unknown command {cmd}")


class CommandsQueue:
    TASKS_QUEUE = "tasks_queue"

    def __init__(self):
        self.redis_connection = Redis()

    def dequeue_cmd(self):
        _, data = self.redis_connection.brpop(self.TASKS_QUEUE)

        return _deserialize_command(data)

    def enqueue_cmd(self, command):
        self.redis_connection.lpush(self.TASKS_QUEUE, command.serialize())
