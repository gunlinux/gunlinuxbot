from datetime import datetime


class User:
    id_: int
    username: str
    last_mssg: datetime
    first_mssg: datetime
    messages_count: int = 0

    def __init__(self, id_, username):
        self.id_ = id_
        self.username = username
        self.first_mssg = datetime.now()

    def new_mssg(self):
        self.messages_count += 1
        self.last_mssg = datetime.now()

    def __str__(self):
        return f'<{self.id}> {self.username} [{self.messages_count}]'

    def __repr__(self):
        return self.__str__()
