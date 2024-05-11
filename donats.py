import json
import logging
import socketio
from typing import TYPE_CHECKING, Optional

from dotenv import load_dotenv
from gunlinuxbot.handlers import HandlerEvent

if TYPE_CHECKING:
    from gunlinuxbot.handlers import DonatHandler

load_dotenv()
logger = logging.getLogger(__name__)


class DonatApi:

    async def run(self):
        logger.critical("rconnect")
        await self.sio.connect(
            "wss://socket.donationalerts.ru:443", transports="websocket"
        )
        logger.critical("rwait")
        await self.sio.wait()
        logger.critical("down")

    def __init__(self, token, handler=None):
        self.sio = socketio.AsyncClient()

        self.token = token
        self.handler: Optional['DonatHandler'] = handler

        @self.sio.on("connect")
        async def on_connect() -> None:
            await self.sio.emit(
                "add-user", {"token": self.token, "type": "alert_widget"}
            )
            if not self.sio.connected:
                logger.critical("connected failed")
                return
            logger.critical("connected")

        @self.sio.event
        async def message(data):  # pylint: disable=unused-argument
            logger.debug("i received a message! len: %s", len(data))

        @self.sio.on("*")
        async def catch_all(event, data):
            logger.debug("catch_all %s", event)

        @self.sio.on("donation")
        async def on_message(data):
            print("on_message")
            data = json.loads(data)
            event = HandlerEvent(
                alert_type=data['alert_type'],
                amount_formatted=data['amount_formatted'],
                mssg=data['message'],
                user=data['username'],
                currency=data['currency'],
            )
            print(event)
            if self.handler is not None:
                return await self.handler.handle_event(event)
            logger.critical('no handler wtf')
