import os


from tasks.taskaction import TaskAction
from tasks.repository import engine


if __name__ == '__main__':

    def start_func():
        _ = os.system('/home/loki/scripts/shutdown.sh')  # noqa: S605
        print('doing staff')

    action = TaskAction(
        engine=engine,
        name='shutdown',
        start=start_func,
    )
    action.execute()
