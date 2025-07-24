import time
from collections.abc import Callable
import typing

from sqlmodel import Session
from sqlalchemy.engine import Engine
from tasks.models import Task
from tasks.repository import TaskRepository

# 🧪 Step 4: Demonstrate usage of the repository


class TaskAction:
    def __init__(
        self,
        name: str,
        engine: Engine,
        duration: int = 0,
        start: Callable | None = None,
        finish: Callable | None = None,
    ):
        self.name = name
        self.duration = duration
        self._start = start
        self._finish = finish
        self.engine = engine

    def execute(self) -> None:
        with Session(self.engine, expire_on_commit=True) as session:
            self.repo = TaskRepository(session)
            active_task = self.start()
            if active_task:
                return

            new_task = Task(title=self.name, duration=self.duration)
            self.repo.add(new_task)
            self.repo.session.commit()
            finish_task = self.wait(new_task)
            self.finish(finish_task)
            return

    def start(self) -> Task | None:
        print('start')
        # checks if have active task
        active_task = self.repo.get_active_by_name(title=self.name)
        if active_task:
            print('already have active task wtf', active_task)
            active_task.duration += self.duration
            self.repo.update(active_task)
            return active_task
        if self._start:
            self._start()
        return None

    def wait(self, new_task: Task) -> Task:
        print('start wait')
        ending = new_task.timestamp + self.duration
        retask: Task | None = None
        while time.time() < ending:
            print('wait in loop')
            time.sleep(new_task.duration)
            with Session(self.engine) as new_session:
                self.repo = TaskRepository(new_session)
                retask = typing.cast('Task', self.repo.get_by_id(new_task.id))
                ending = retask.timestamp + retask.duration
        if retask:
            return retask
        return new_task

    def finish(self, new_task: Task) -> None:
        print('start finish')
        if self._finish:
            self._finish()
        new_task.completed = True
        self.repo.update(new_task)
