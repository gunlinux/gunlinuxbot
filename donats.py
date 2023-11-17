import json
import socketio
from datetime import datetime

from dotenv import load_dotenv
from models.events import Event
load_dotenv()


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

    async def default_handler_function(self, event):
        mssg = f'''{event.username} пожертвовал {event.amount_formatted}
                    {event.currency} | {event.message}'''
        print(mssg)

    def __init__(self, token, handler=None):
        self.sio = socketio.AsyncClient()
        self.token = token
        if handler is None:
            self.handler = None
            self.handler_function = self.default_hanlder_function
        else:
            self.handler = handler

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

            await self.handler.handle_donation_event(
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
