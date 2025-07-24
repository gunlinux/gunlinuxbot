from collections.abc import Mapping
from marshmallow import Schema, fields, validate, INCLUDE, post_load, EXCLUDE
from marshmallow_enum import EnumField

from dataclasses import dataclass, asdict
from enum import StrEnum
from gunlinuxbot.models import Event
import typing


from retwitch.models import TokenResponse


class EventType(StrEnum):
    CHANNEL_FOLLOW = 'channel.follow'
    CHANNEL_RAID = 'channel.raid'
    CHANNEL_MESSAGE = 'channel.chat.message'
    CHANNEL_SUBSCRIBE = 'channel.subscribe'
    CHANNEL_RESUBSCRIBE = 'channel.subscription.message'
    CUSTOM_REWARD = 'channel.channel_points_custom_reward_redemption.add'


@dataclass
class RetwitchEvent(Event):
    event_type: EventType
    user_id: str
    user_login: str
    user_name: str
    event: dict[str, typing.Any]

    @property
    def message(self) -> str | None:
        return None


class RetwitchEventSchema(Schema):
    event_type = EnumField(EventType, by_value=True, required=True)
    user_id = fields.Str(required=False, allow_none=True)
    user_login = fields.Str(required=False, allow_none=True)
    user_name = fields.Str(required=False, allow_none=True)
    event = fields.Dict(keys=fields.Str(), values=fields.Raw(allow_none=True))

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_obj(self, data: Mapping[str, typing.Any], **_):
        return RetwitchEvent(**data)


class EventRaid(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return f'{self.user_name} just raid channel with {self.event["viewers"]}'


class EventCustomReward(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return f'{self.user_name} took reward {self.event}'


class EventChannelFollow(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return f'{self.user_name} followed channel'


class EventChannelMessage(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return self.event.get('text', '')


class EventChannelSubscribe(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return f'{self.user_name} just subscribed to channel ({self.event.get("tier")})'


class EventChannelResubscribeMessage(RetwitchEvent):
    @property
    @typing.override
    def message(self) -> str | None:
        return (
            f'{self.user_name} just resubscribed to channel '
            f'({self.event.get("tier")}) with message {self.event.get("text")}'
        )


def create_event_from_subevent(data: Mapping[str, typing.Any]) -> RetwitchEvent | None:
    sub_type = data.get('metadata', {}).get('subscription_type', None)
    event_type = EventType(sub_type)
    event = data.get('payload', {}).get('event', {})
    match event_type:
        case EventType.CHANNEL_RAID:
            return EventRaid(
                event_type=event_type,
                user_id=event['from_broadcaster_user_id'],
                user_login=event['from_broadcaster_user_login'],
                user_name=event['from_broadcaster_user_name'],
                event={'viewers': event['viewers']},
            )

        case EventType.CUSTOM_REWARD:
            return EventCustomReward(
                event_type=event_type,
                user_id=event['user_id'],
                user_login=event['user_login'],
                user_name=event['user_name'],
                event={
                    'status': event.get('status', ''),
                    'user_input': event.get('user_input', ''),
                    'title': event.get('reward', {}).get('title'),
                    'cost': event.get('reward', {}).get('cost'),
                },
            )

        case EventType.CHANNEL_FOLLOW:
            return EventChannelFollow(
                event_type=event_type,
                user_id=event['user_id'],
                user_login=event['user_login'],
                user_name=event['user_name'],
                event={},
            )
        case EventType.CHANNEL_MESSAGE:
            return EventChannelMessage(
                event_type=event_type,
                user_id=event['chatter_user_id'],
                user_login=event['chatter_user_login'],
                user_name=event['chatter_user_name'],
                event={
                    'text': event['message'].get('text', '')
                    if event.get('message')
                    else '',
                    'message_type': event.get('message_type', ''),
                    'reply': event.get('reply', None),
                    'channel_points_custom_reward_id': event.get(
                        'channel_points_custom_reward_id'
                    ),
                },
            )
        case EventType.CHANNEL_SUBSCRIBE:
            return EventChannelSubscribe(
                event_type=event_type,
                user_id=event['user_id'],
                user_login=event['user_login'],
                user_name=event['user_name'],
                event={
                    'tier': event.get('tier'),
                    'is_gift': event.get('is_gift', False),
                },
            )
        case EventType.CHANNEL_RESUBSCRIBE:
            return EventChannelResubscribeMessage(
                event_type=event_type,
                user_id=event['user_id'],
                user_login=event['user_login'],
                user_name=event['user_name'],
                event={
                    'text': event['message'].get('text', '')
                    if event.get('message')
                    else '',
                    'tier': event.get('tier'),
                    'cumulative_months': event.get('cumulative_months', 0),
                    'streak_months': event.get('streak_months'),
                    'duration_months': event.get('duration_months', 0),
                },
            )


class MetadataSchema(Schema):
    message_id = fields.Str(required=True)
    message_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                'session_welcome',
                'notification',
                'session_keepalive',
                'session_reconnect',
                'revocation',
            ]
        ),
    )
    message_timestamp = fields.DateTime(required=True)

    # Optional fields for notification type
    subscription_type = fields.Str(required=False)
    subscription_version = fields.Str(required=False)

    class Meta:
        unknown = INCLUDE


class SessionSchema(Schema):
    id = fields.Str(required=True)
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['connected', 'disconnected', 'reconnecting']),
    )
    connected_at = fields.DateTime(required=True)
    keepalive_timeout_seconds = fields.Int(required=False, allow_none=True)
    reconnect_url = fields.Str(required=False, allow_none=True)
    recovery_url = fields.Str(required=False, allow_none=True)

    class Meta:
        unknown = INCLUDE


class PayloadSchema(Schema):
    session = fields.Nested(SessionSchema, required=False)

    # Add other possible payload fields here if needed
    class Meta:
        unknown = INCLUDE


class EventSchema(Schema):
    metadata = fields.Nested(MetadataSchema, required=True)
    payload = fields.Nested(PayloadSchema, required=True)

    class Meta:
        unknown = INCLUDE


class TokenResponseSchema(Schema):
    access_token = fields.Str(required=True)
    expires_in = fields.Int(required=True)
    token_type = fields.Str(required=True)
    refresh_token = fields.Str(required=False)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def create_model(self, data: dict[str, typing.Any], **_) -> TokenResponse:
        return TokenResponse(**data)


def promote_event(event: RetwitchEvent) -> RetwitchEvent:
    mapping: dict[EventType, type[RetwitchEvent]] = {
        EventType.CHANNEL_FOLLOW: EventChannelFollow,
        EventType.CHANNEL_RAID: EventRaid,
        EventType.CHANNEL_RESUBSCRIBE: EventChannelResubscribeMessage,
        EventType.CHANNEL_SUBSCRIBE: EventChannelSubscribe,
        EventType.CUSTOM_REWARD: EventCustomReward,
        EventType.CHANNEL_MESSAGE: EventChannelMessage,
    }

    cls = mapping.get(event.event_type, RetwitchEvent)
    return cls(**asdict(event))
