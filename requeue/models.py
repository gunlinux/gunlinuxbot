from dataclasses import dataclass, asdict
from enum import Enum, auto
import typing


class QueueMessageStatus(Enum):
    WAITING = auto()
    PROCESSING = auto()
    FINISHED = auto()
    DROPED = auto()


@dataclass
class QueueMessage:
    event: str
    data: str
    source: str = ''
    retry: int = 0
    status: QueueMessageStatus = QueueMessageStatus.WAITING

    def to_serializable_dict(self) -> dict[str, typing.Any]:
        return {
            field: (value.value if isinstance(value, Enum) else value)
            for field, value in asdict(self).items()
        }


if __name__ == '__main__':
    queue_message = QueueMessage(event='test_event', data='{"data": "some_data"}')
    queue_message_dict = queue_message.to_serializable_dict()
    print(queue_message_dict)
