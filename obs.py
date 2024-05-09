import os
import time

from obswebsocket import obsws, requests  # noqa: E402
from dotenv import load_dotenv


load_dotenv()


class Obs:
    def __init__(self):
        host = os.environ.get("OBS_HOST", "localhost")
        port = int(os.environ.get("OBS_PORT", 4455))
        password = os.environ.get("OBS_PASSWORD")
        self.ws = obsws(host, port, password)

    def connect(self):
        self.ws.connect()

    def disconnect(self):
        self.ws.disconnect()

    def call(self, *args, **kwargs):
        self.ws.call(*args, **kwargs)


def dasha_show():
    obs = Obs()
    obs.connect()
    obs.call(requests.GetSceneItemList(sceneName="dasha_scene"))
    obs.call(
        requests.SetSceneItemEnabled(
            sceneName="dasha_scene", sceneItemId=1, sceneItemEnabled=True
        )
    )
    obs.disconnect()


def pasha_help_show():

    obs = Obs()
    obs.connect()
    print(obs.call(requests.GetSceneItemList(sceneName="pasha_help")))
    print(obs.call(
        requests.SetSceneItemEnabled(
            sceneName="pasha_help", sceneItemId=1, sceneItemEnabled=True
        )
    ))
    time.sleep(9)
    print(obs.call(
        requests.SetSceneItemEnabled(
            sceneName="pasha_help", sceneItemId=1, sceneItemEnabled=False
        )
    ))
    obs.disconnect()


def dasha_hide():
    obs = Obs()
    obs.connect()
    obs.call(requests.GetSceneItemList(sceneName="dasha_scene"))
    obs.call(
        requests.SetSceneItemEnabled(
            sceneName="dasha_scene", sceneItemId=1, sceneItemEnabled=False
        )
    )
    obs.disconnect()

if __name__ == '__main__':
    pasha_help_show()
