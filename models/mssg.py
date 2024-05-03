from datetime import datetime


class Event:
    id_: int
    timestamp: datetime
    user_id: int

    def __init__(self, id_, user_id):
        self.user_id = user_id
        self.id_ = id_
        self.timestamp = datetime.now()

    def __str__(self):
        return f'<{self.id_}> [{self.timestamp}]'

    def __repr__(self):
        return self.__str__()


class Mssg(Event):
    mssg: str

    def __init__(self, id_, mssg, user_id):
        super().__init__(id_=id_, user_id=user_id)
        self.mssg = mssg

    def __str__(self):
        return f'<{self.id_}> [{self.timestamp}]: {self.mssg}'

    def __repr__(self):
        return self.__str__()
