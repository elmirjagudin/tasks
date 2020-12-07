from json import dumps, loads
from redis import Redis


class JsonSerializable:
    def serialize(self):
        return dumps(self._as_dict())


class RunningTask(JsonSerializable):
    def __init__(self, name, stdlog, errlog):
        self.name = name
        self.stdlog = stdlog
        self.errlog = errlog

    def _as_dict(self):
        return {"name": self.name, "stdlog": self.stdlog, "errlog": self.errlog}


class StartTask(JsonSerializable):
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


class CancelTask(JsonSerializable):
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


class TasksMQ:
    TASKS_QUEUE = "tasks:enqueued"
    RUNNING_TASKS = "tasks:running"

    def __init__(self):
        self.redis_connection = Redis()

    def enqueue_task_command(self, command):
        self.redis_connection.lpush(self.TASKS_QUEUE, command.serialize())

    def dequeue_task_command(self):
        _, data = self.redis_connection.brpop(self.TASKS_QUEUE)

        return _deserialize_command(data)

    def add_running_task(self, task_id, running_task):
        self.redis_connection.hset(
            self.RUNNING_TASKS, task_id, running_task.serialize()
        )

    def get_running_tasks(self):
        return self.redis_connection.hgetall(self.RUNNING_TASKS)
