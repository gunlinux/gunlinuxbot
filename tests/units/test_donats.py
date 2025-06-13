from dataclasses import asdict
import json
from typing import TYPE_CHECKING
import typing
from donats.schemas import AlertEventSchema
from requeue.schemas import QueueMessageSchema
from requeue.rredis import Connection
from requeue.requeue import Queue

if TYPE_CHECKING:
    from donats.models import AlertEvent
    from requeue.models import QueueMessage


async def test_donat_route(mock_redis: Connection):
    raw_event = {
        'id': 162020502,
        'alert_type': '1',
        'is_shown': '0',
        'additional_data': '{"randomness":666}',
        'billing_system': 'fake',
        'billing_system_type': None,
        'username': 'test1',
        'amount': '1.00',
        'amount_formatted': '1',
        'amount_main': 1,
        'currency': 'RUB',
        'message': '1',
        'header': '',
        'date_created': '2025-02-26 16:25:58',
        'emotes': None,
        'ap_id': None,
        '_is_test_alert': True,
        'message_type': 'text',
        'preset_id': 0,
    }

    message: AlertEvent = typing.cast('AlertEvent', AlertEventSchema().load(raw_event))
    message_dict = asdict(message)
    _ = message_dict.get('id', None)
    message_dict['alert_type'] = '1'
    message_dict['billing_system'] = 'fake'
    payload = {
        'event': 'da_message',
        'data': json.dumps(message_dict),
    }
    queue_message: QueueMessage = typing.cast(
        'QueueMessage', QueueMessageSchema().load(payload)
    )
    async with mock_redis as connection:
        queue = Queue(name='test_queue', connection=connection)
        await queue.push(queue_message)
        assert await queue.pop()
