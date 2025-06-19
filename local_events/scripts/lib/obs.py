import typing
from obswebsocket import obsws, requests


class ObsClient:
    def __init__(
        self, host: str = 'localhost', port: int = 4455, password: str = ''
    ) -> None:
        self._host: str = host
        self._password: str = password if password else 'bPorasbO5br566Pk'
        self._port: int = port
        self.client = obsws(self._host, self._port, self._password)
        self.client.connect()

    def connect(self):
        self.client.connect()

    def version(self) -> None:
        version = self.client.call(requests.GetVersion()).getObsVersion()
        return version

    def getScenes(self):
        scenes = self.client.call(requests.GetSceneList())
        return scenes.getScenes()

    def GetSceneItemList(self, sceneName: str) -> list[typing.Any]:
        return self.client.call(requests.GetSceneItemList(sceneName=sceneName)).getsceneItems()

    def SetSourceFilterEnabled(
        self, sourceName: str, filterName: str, filterEnabled: bool = True
    ) -> None:
        _ = self.client.call(
            requests.SetSourceFilterEnabled(
                sourceName=sourceName,
                filterName=filterName,
                filterEnabled=filterEnabled,
            )
        )
    def SceneItemEnableStateChanged(self,  sceneName: str, sceneItemId: int, sceneItemEnabled: bool) -> None:
        temp = self.client.call(requests.SetSceneItemEnabled(
            sceneName=sceneName, sceneItemId=sceneItemId, sceneItemEnabled=sceneItemEnabled))
        print('mytemp')
        print(temp)

    def GetSourceFilter(self, filter_name: str, source_uuid: int) -> int | None:
        item = self.client.call(
            requests.GetSourceFilter(sourceUuid=source_uuid, filterName=filter_name)
        )
        if item:
            print(item)
            try:
                return item.getfilterIndex()
            except KeyError:
                return None

    def disconnect(self):
        self.client.disconnect()
