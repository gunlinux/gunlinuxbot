import json
import logging
from enum import Enum
from typing import cast, override
import typing

from donats.models import AlertEvent
from donats.schemas import AlertEventSchema
from requeue.models import QueueMessage
from gunlinuxbot.models import Event
from gunlinuxbot.handlers import EventHandler

from gunlinuxbot.utils import logger_setup


logger = logger_setup('gunlinuxbot.handlers')
logger.setLevel(logging.DEBUG)


class DonationAlertTypes(Enum):
    DONATION = 1
    CUSTOM_REWARD = 19
    FOLLOW = 6
    SUBSCRIBE = 7


class DonatEventHandler(EventHandler):
    @typing.override
    async def on_message(self, message: QueueMessage) -> QueueMessage | None:
        logger.debug('Processing new event from queue')
        data_json = json.loads(message.data)
        logger.debug('Received message data: %s', data_json)
        event: AlertEvent = cast('AlertEvent', AlertEventSchema().load(data_json))
        logger.debug('Processed event: %s', event)
        try:
            await self.handle_event(event)
        except Exception as e:  # noqa: BLE001
            logger.critical('FAILED TO PROCESS MESSAGE %s %s ', message, e)
            return message

    @typing.override
    async def handle_event(self, event: Event) -> None:  # pyright: ignore[reportRedeclaration]
        event: AlertEvent = cast('AlertEvent', event)

        if event.alert_type == DonationAlertTypes.DONATION.value:
            await self._donation(event)
            return

        if event.alert_type == DonationAlertTypes.CUSTOM_REWARD.value:
            await self._custom_reward(event)
            return

        if event.alert_type == DonationAlertTypes.FOLLOW.value:
            await self._follow(event)
            return

        if event.alert_type == DonationAlertTypes.SUBSCRIBE.value:
            await self._subscribe(event)
            return

        logger.warning('handle_event not implemented yet %s', event)
        return

    async def _donation(self, event: AlertEvent) -> None:
        logger.info('donat.event _donation')
        if event.username is None:
            event.username = 'anonym'
        mssg_text = f"""{self.admin} {event.username} пожертвовал
            {event.amount_formatted} {event.currency} | {event.message}"""
        await self.chat(mssg_text)

    async def _follow(self, event: AlertEvent) -> None:
        logger.info('donat.event _follow')
        mssg_text = f'@gunlinux @{event.username} started follow auf'
        await self.chat(mssg_text)

    async def _subscribe(self, event: AlertEvent) -> None:
        logger.info('donat.event _subscribe (youtube?)')
        mssg_text = f'@gunlinux @{event.username} _subscribed on youtube <3 auf'
        await self.chat(mssg_text)

    async def _custom_reward(self, event: AlertEvent) -> None:
        logger.info('donat.event _custom_reward %s', event)
        await self.run_command(event)

    @override
    async def run_command(self, event: AlertEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        logger.debug('Running command for event %s', event)
        # test it
        for command_name, command in self.commands.items():
            if event.message.startswith('$'):
                # ignoring admin syntax
                logger.info('ignoring admin command %s')
                continue

            if event.message.startswith(command_name.lower()):
                logger.debug('detected command: %s', command)
                mssg = await command.run(event)
                if mssg:
                    await self.chat(mssg)
                break
        else:
            await self.chat(f'{event.username} взял награду {event.message}')
