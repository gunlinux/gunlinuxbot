import json
import logging
import typing

from retwitch.schemas import (
    RetwitchEvent,
    EventType,
    RetwitchEventSchema,
    promote_event,
)
from requeue.models import QueueMessage
from gunlinuxbot.models import Event
from gunlinuxbot.handlers import EventHandler

from gunlinuxbot.utils import logger_setup


logger = logger_setup('gunlinuxbot.handlers')
logger.setLevel(logging.DEBUG)


class RetwitchEventHandler(EventHandler):
    @typing.override
    async def on_message(self, message: QueueMessage) -> QueueMessage | None:
        logger.debug('Processing new event from queue')
        data_json = json.loads(message.data)
        logger.debug('Received message data: %s', data_json)
        event: RetwitchEvent = typing.cast(
            'RetwitchEvent', RetwitchEventSchema().load(data_json)
        )
        logger.debug('Processed event: %s', event)
        try:
            await self.handle_event(event)
        except Exception as e:  # noqa: BLE001
            logger.critical('FAILED TO PROCESS MESSAGE %s %s ', message, e)
            return message

    @typing.override
    async def handle_event(self, event: Event) -> None:
        event = typing.cast('RetwitchEvent', event)
        # route event here by type
        new_event = promote_event(event)
        if new_event.event_type == EventType.CHANNEL_FOLLOW:
            await self._follow(new_event)

        if new_event.event_type == EventType.CHANNEL_SUBSCRIBE:
            await self._subscribe(new_event)

        if new_event.event_type == EventType.CHANNEL_RESUBSCRIBE:
            await self._resubscribe(new_event)

        if new_event.event_type == EventType.CHANNEL_RAID:
            await self._channel_raid(new_event)

        if new_event.event_type == EventType.CUSTOM_REWARD:
            await self.run_command(new_event)

    async def _follow(self, event: RetwitchEvent) -> None:
        logger.info('donat.event _follow')
        if event.message:
            await self.chat(event.message)

    async def _subscribe(self, event: RetwitchEvent) -> None:
        logger.info('donat.event _subscribe')
        if event.message:
            await self.chat(event.message)

    async def _resubscribe(self, event: RetwitchEvent) -> None:
        logger.info('donat.event _resubscribe')
        if event.message:
            await self.chat(event.message)

    async def _channel_raid(self, event: RetwitchEvent) -> None:
        logger.info('donat.event _channel_raid')
        if event.message:
            await self.chat(event.message)

    async def _custom_reward(self, event: RetwitchEvent) -> None:
        logger.info('donat.event _custom_reward %s', event)
        if event.message:
            await self.chat(event.message)

    @typing.override
    async def run_command(self, event: Event) -> None:
        pass
