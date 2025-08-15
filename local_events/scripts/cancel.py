import sys

from sqlmodel import Session
from tasks.repository import engine, TaskRepository  # pyright: ignore[reportImplicitRelativeImport]
from tasks.models import TaskStatus  # pyright: ignore[reportImplicitRelativeImport]


def usage() -> None:
    print('{sys.argv[0]} <task_name>')
    print('for cancel all task')


if __name__ == '__main__':
    if len(sys.argv) != 1 + 1:
        usage()
        sys.exit(1)
    name = sys.argv[1]

    with Session(engine, expire_on_commit=True) as session:
        repo = TaskRepository(session)
        tasks = repo.get_all_active_by_name(name)
        print(f'found {len(tasks)}) tasks')
        for task in tasks:
            task.completed = TaskStatus.CANCELED.value
            repo.update(task)
