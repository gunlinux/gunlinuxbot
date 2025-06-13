import json
import logging
from collections.abc import Callable, Coroutine, Mapping
from typing import Any, cast

import socketio
from marshmallow.exceptions import ValidationError

from gunlinuxbot.models.event import Event
from donats.models import AlertEvent
from donats.schemas import AlertEventSchema

logger = logging.getLogger(__name__)


class DonatApi:
    async def run(self) -> None:
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

        @self.sio.on('connect')  # pyright: ignore[reportOptionalCall,reportUntypedFunctionDecorator]
        async def on_connect() -> None:  # pyright: ignore[reportUnusedFunction]
            await self.sio.emit(
                'add-user',
                {'token': self.token, 'type': 'alert_widget'},
            )

        @self.sio.event
        async def message(data: str) -> None:
            logger.debug('i received a message! len: %s', len(data))

        @self.sio.on('*')  # pyright: ignore[reportOptionalCall]
        async def catch_all(event: AlertEvent, data: str) -> None:
            logger.debug('catch_all %s %s', event, len(data))

        @self.sio.on('donation')  # pyright: ignore[reportOptionalCall]
        async def on_message(message_data: str) -> None:
            data: Mapping = json.loads(message_data)
            logger.debug('new event %s', data)
            try:
                event: AlertEvent = cast('AlertEvent', AlertEventSchema().load(data))
            except ValidationError:
                logger.debug('ghost message, cause donation alerts hates me %s', data)
                return None
            if self.handler is not None:
                return await self.handler(event)
            logger.critical('no handler wtf')
            return None
