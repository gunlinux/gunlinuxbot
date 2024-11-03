import json
import logging
import socketio
from typing import TYPE_CHECKING, Optional

from dotenv import load_dotenv
from ..handlers import  HandlerEvent

load_dotenv()
logger = logging.getLogger(__name__)


class DonatApi:

    async def run(self):
        logger.critical("rconnect")
        await self.sio.connect(
            "wss://socket.donationalerts.ru:443", transports="websocket"
        )
        await self.sio.wait()

    def __init__(self, token, handler=None):
        self.sio = socketio.AsyncClient()

        self.token = token
        self.handler: Optional["DonatHandler"] = handler

        @self.sio.on("connect")
        async def on_connect() -> None:
            await self.sio.emit(
                "add-user", {"token": self.token, "type": "alert_widget"}
            )

        @self.sio.event
        async def message(data):  # pylint: disable=unused-argument
            logger.debug("i received a message! len: %s", len(data))

        @self.sio.on("*")
        async def catch_all(event, data):
            logger.debug("catch_all %s", event)

        @self.sio.on("donation")
        async def on_message(data):
            data = json.loads(data)
            event = HandlerEvent(
                alert_type=data["alert_type"],
                amount_formatted=data["amount_formatted"],
                mssg=data["message"],
                user=data["username"],
                currency=data["currency"],
            )
            logger.debug("donat on_message %s", event)
            if self.handler is not None:
                return await self.handler(event)
            logger.critical("no handler wtf")
