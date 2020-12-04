from celery import Celery
from subprocess import run

app = Celery("tasks", broker="redis://localhost")


@app.task
def add(x, y):
    return x + y


@app.task
def hydra(level):
    run(["./hydra.py", str(level)])
