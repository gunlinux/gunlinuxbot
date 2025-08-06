import os

from tasks.taskaction import TaskAction
from tasks.repository import engine


if __name__ == '__main__':
    mouse = 'logitech-usb-receiver'

    def start_func():
        print('doing staff')
        _ = os.system(f'hyprctl keyword device[{mouse}]:enabled false')  # noqa: S605

    def finish_func():
        print('endinshg staff')
        _ = os.system(f'hyprctl keyword device[{mouse}]:enabled true')  # noqa: S605
        _ = os.system('/home/loki/scripts/mssg.sh "Мышка снова жива"')  # noqa: S605

    action = TaskAction(
        engine=engine,
        name='mouseoff',
        duration=60 * 5,
        start=start_func,
        finish=finish_func,
    )
    action.execute()
