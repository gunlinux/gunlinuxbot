from datetime import datetime


class Event:
    id: int
    timestamp: datetime
    user_id: int

    def __init__(self, id, user_id):
        self.user_id = user_id
        self.id = id
        self.timestamp = datetime.now()

    def __str__(self):
        return f'<{self.id}> [{self.timestamp}]'

    def __repr__(self):
        return self.__str__()


class Mssg(Event):
    mssg: str

    def __init__(self, id, mssg, user_id):
        super().__init__(id=id, user_id=user_id)
        self.mssg = mssg

    def __str__(self):
        return f'<{self.id}> [{self.timestamp}]: {self.mssg}'

    def __repr__(self):
        return self.__str__()



