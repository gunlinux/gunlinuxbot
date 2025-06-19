from tasks.taskaction import TaskAction
from tasks.repository import engine


if __name__ == '__main__':

    def start_func():
        print('doing staff')

    def finish_func():
        print('endinshg staff')

    action = TaskAction(
        engine=engine,
        name='mouseoff',
        duration=5,
        start=start_func,
        finish=finish_func,
    )
    action.execute()
