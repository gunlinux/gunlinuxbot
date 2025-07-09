import json
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Mapping
from pathlib import Path
from retwitch.schemas import EventSchema, EventType
from retwitch.schemas import create_event_from_subevent

path = Path('tests/data/data_events.json')
with path.open() as f:
    data_events = json.load(f)


def test_basic_twitch_events():
    for event in data_events:
        new_event = typing.cast('Mapping[str, typing.Any]', EventSchema().load(event))
        assert new_event


def test_process_events():
    for event in data_events:
        new_event = typing.cast('Mapping[str, typing.Any]', EventSchema().load(event))
        assert new_event
        sub_type = new_event.get('metadata', {}).get('subscription_type', None)
        if not sub_type:
            continue

        if sub_type == EventType.CHANNEL_RAID:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert new_event.message == 'gunlinux_bot just raid channel with 1'
            return

        if sub_type == EventType.CUSTOM_REWARD:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert (
                new_event.message
                == "gunlinux took reward {'status': 'unfulfilled', 'user_input': '', 'title': 'flashback', 'cost': 1}"
            )
            return

        if sub_type == EventType.CHANNEL_FOLLOW:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert new_event.message == 'gunlinux_bot followed channel'
            return

        if sub_type == EventType.CHANNEL_MESSAGE:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert new_event.message == 'theG4NS just typed auf'
            return

        if sub_type == EventType.CHANNEL_SUBSCRIBE:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert new_event.message == 'Cool_User just subscribed to channel (1000)'
            return

        if sub_type == EventType.CHANNEL_RESUBSCRIBE:
            new_event = create_event_from_subevent(new_event)
            assert new_event
            assert (
                new_event.message
                == 'Cool_User just resubscribed to channel (1000) with message Love the stream! FevziGG'
            )
