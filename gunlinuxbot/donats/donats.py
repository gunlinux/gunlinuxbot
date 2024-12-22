import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import socketio
from dotenv import load_dotenv

from gunlinuxbot.handlers import Event

load_dotenv()
logger = logging.getLogger(__name__)


class DonatApi:
    async def run(self) -> None:
        logger.critical('rconnect')
        await self.sio.connect(
            'wss://socket.donationalerts.ru:443',
            transports='websocket',
        )
        await self.sio.wait()

    def __init__(self, token: str, handler: Callable[[Event], Coroutine[Any, Any, None]]) -> None:
        self.sio = socketio.AsyncClient()

        self.token: str = token
        self.handler: Callable[[Event], Coroutine[Any, Any, None]] = handler

        @self.sio.on('connect')
        async def on_connect() -> None:
            await self.sio.emit(
                'add-user',
                {'token': self.token, 'type': 'alert_widget'},
            )

        @self.sio.event
        async def message(data: str) -> None:
            logger.debug('i received a message! len: %s', len(data))

        @self.sio.on('*')
        async def catch_all(event: Event, data: str) -> None:
            logger.debug('catch_all %s %s', event, len(data))

        @self.sio.on('donation')
        async def on_message(data: str) -> None:
            data = json.loads(data)
            logger.critical('new event %s', data)
            event: Event = Event(
                id=int(data['id']),
                alert_type=int(data['alert_type']),
                amount_formatted=data['amount_formatted'],
                mssg=data['message'],
                user=data['username'],
                currency=data['currency'],
            )
            logger.debug('donat on_message %s', event)
            if self.handler is not None:
                await self.handler(event)
            logger.critical('no handler wtf')
