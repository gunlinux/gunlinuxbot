import json
import logging
from collections.abc import Callable, Coroutine, Mapping
from typing import Any, cast

import socketio
from dotenv import load_dotenv
from marshmallow.exceptions import ValidationError

from gunlinuxbot.models.event import Event
from gunlinuxbot.models.donats import AlertEvent
from gunlinuxbot.schemas.donats import AlertEventSchema

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

    def __init__(
        self, token: str, handler: Callable[[Event], Coroutine[Any, Any, None]]
    ) -> None:
        self.sio: socketio.AsyncClient = socketio.AsyncClient()

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

        @self.sio.on('*')  # pyright: ignore[reportOptionalCall]
        async def catch_all(event: AlertEvent, data: str) -> None:
            logger.critical('catch_all %s %s', event, len(data))

        @self.sio.on('donation')  # pyright: ignore[reportOptionalCall]
        async def on_message(message_data: str) -> None:
            data: Mapping = json.loads(message_data)
            logger.critical('new event %s', data)
            try:
                event: AlertEvent = cast('AlertEvent', AlertEventSchema().load(data))
            except ValidationError:
                logger.debug('ghost message, cause donation alerts hates me %s', data)
                return None
            if self.handler is not None:
                return await self.handler(event)
            logger.critical('no handler wtf')
            return None
