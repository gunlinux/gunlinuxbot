from dataclasses import asdict
import json
from typing import TYPE_CHECKING
from gunlinuxbot.schemas.donats import AlertEventSchema
from gunlinuxbot.schemas.myqueue import QueueMessageSchema
from gunlinuxbot.myqueue import Queue
from datetime import datetime
if TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage


async def test_donat_route(mock_redis):
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

    message = AlertEventSchema().load(raw_event)
    message_dict = asdict(message)
    message_dict.get('id', None)
    message_dict['alert_type'] = '1'
    message_dict['billing_system'] = 'fake'
    payload = {
        'event': 'da_message',
        'timestamp': datetime.now().isoformat(),
        'data': json.dumps(message_dict),
    }
    queue_message: QueueMessage = QueueMessageSchema().load(payload)
    queue = Queue(name='test_queue', connection=mock_redis)
    await queue.push(queue_message)
    assert await queue.pop()
