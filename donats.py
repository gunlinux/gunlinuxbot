import os
import json
import asyncio
import socketio
from datetime import datetime
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
load_dotenv()


@dataclass
class Event:
    id: int
    alert_type: str
    is_shown: str
    additional_data: dict
    billing_system: str
    billing_system_type: str
    username: str
    amount: str
    amount_formatted: str
    amount_main: int
    currency: str
    message: str
    header: str
    date_created: Any
    emotes: str
    ap_id: str
    _is_test_alert: bool
    message_type: str
    preset_id: int
    objects: dict


class DonatApi:
    sio = None
    token = None
    handler = None

    async def run(self):
        print('rconnect')
        await self.sio.connect("wss://socket.donationalerts.ru:443", transports="websocket")
        print('rwait')
        await self.sio.wait()
        print('end')

    async def default_handler(self, event):
         print(f"{event.username} пожертвовал {event.amount_formatted} {event.currency} | {event.message}")

    def __init__(self, token, handler=None):
        self.sio = socketio.AsyncClient()
        self.token = token
        if handler is None:
            self.handler = self.default_handler

        @self.sio.on("connect")
        async def on_connect():
            print('connect')
            await self.sio.emit("add-user", {"token": self.token, "type": "alert_widget"})
            print('emit')

        @self.sio.event
        async def message(data):
            print('i received a message!')

        @self.sio.on('*')
        async def catch_all(event, data):
            print('cats all')
            print(f'{event} {data}')

        @self.sio.on("donation")
        async def on_message(data):
            print('on_message')
            data = json.loads(data)
            print(f"date failed = {data['date_created']}")
            await self.handler(
                Event(
                    data["id"],
                    data["alert_type"],
                    data["is_shown"],
                    json.loads(data["additional_data"]),
                    data["billing_system"],
                    data["billing_system_type"],
                    data["username"],
                    data["amount"],
                    data["amount_formatted"],
                    data["amount_main"],
                    data["currency"],
                    data["message"],
                    data["header"],
                    datetime.strptime(data["date_created"], "%Y-%m-%d %H:%M:%S"),
                    data["emotes"],
                    data["ap_id"],
                    data["_is_test_alert"],
                    data["message_type"],
                    data.get("preset_id", None),
                    data
                    )
                )


async def main():
    token = os.environ.get('DA_ACCESS_TOKEN', 'set_dame_token')
    print(token)
    donat = DonatApi(token=token, handler=handler)
    await donat.run()


if __name__ == '__main__':
    asyncio.run(main())
