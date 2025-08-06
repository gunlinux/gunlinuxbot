from collections.abc import Mapping, Callable, Awaitable
import asyncio
import typing
import json
from time import time

import aiohttp
from retwitch.schemas import EventSchema, Event, create_event_from_subevent
from retwitch.token import TokenManager
from retwitch.reqs import HttpReqs
from gunlinuxbot.utils import logger_setup

"""
Рекомендация: разделить на минимум три уровня — WebSocket клиент, EventSub подписчик, обработчик событий.
"""

logger = logger_setup('twitchbot')


WS_URL = 'wss://eventsub.wss.twitch.tv/ws?keep_alive_timeout=30'


class BotClient:
    def __init__(
        self,
        token_manager: TokenManager,
        client_id: str,
        user_id: str,
        broadcaster_user_id: str,
        keep_alive_timeout: int = 30,
    ):
        self.http_reqs: HttpReqs = HttpReqs(
            token_manager=token_manager, client_id=client_id
        )
        self.token_manager = token_manager
        self.client_id = client_id
        self._keep_alive_timeout: int = keep_alive_timeout
        self._heartbeat: int = min(self._keep_alive_timeout, 25) + 5
        self.session_id = None
        self.user_id: str = user_id
        self.broadcaster_user_id: str = broadcaster_user_id
        self.lastseen: float | None = None
        self._socket = None
        self.handler: Callable[[Event], Awaitable[None]] | None = None

    async def create_sub(self, session_id: str) -> None:
        await self.http_reqs.create_sub_chat_message(
            session_id=session_id,
            broadcaster_user_id=self.broadcaster_user_id,
            user_id=self.user_id,
        )
        logger.info('channel_follow %s', self.broadcaster_user_id)
        await self.http_reqs.create_sub_channel_follow(
            session_id=session_id,
            broadcaster_user_id=self.broadcaster_user_id,
            user_id=self.user_id,
        )

    async def process_event(self, event: Mapping[str, typing.Any]) -> None:
        if self._socket is None:
            raise ValueError('Dame')
        match event['metadata']['message_type']:
            case 'session_welcome':
                logger.info('got welcome message')
                self.lastseen = time()
                self.session_id = event['payload']['session']['id']

            case 'session_keepalive':
                logger.info('updated last seen')
                self.lastseen = time()

            case 'session_reconnect':
                await self._socket.close()

            case 'revocation':
                await self._socket.close()
            case _:
                new_event: Event | None = create_event_from_subevent(event)
                if not new_event:
                    return
                await self.handler(new_event)

    async def _listen(self):
        logger.info('start listen')
        while 1:
            await asyncio.sleep(self._keep_alive_timeout)
            if self.lastseen is None or not self._socket:
                continue

            if time() - self.lastseen > self._keep_alive_timeout:
                logger.warning('we are dead')
                await self._socket.close()

    async def run(self, handler: Callable[[Event], Awaitable[None]]) -> None:
        self.handler = handler
        await asyncio.gather(self.run_ws(), self._listen())

    async def run_ws(self):
        while True:
            async with aiohttp.ClientSession() as session:
                params = {
                    'keepalive_timeout_seconds': self._keep_alive_timeout,
                }
                self._socket = await session.ws_connect(
                    'wss://eventsub.wss.twitch.tv/ws',
                    heartbeat=self._heartbeat,
                    params=params,
                )
                welcome_message: aiohttp.WSMessage = await self._socket.receive()
                event = typing.cast(
                    'Mapping[str, typing.Any]',
                    EventSchema().load(json.loads(welcome_message.data)),
                )
                await self.process_event(event)
                if not self.session_id:
                    raise ValueError('no_session_id')
                subs = await self.http_reqs.get_subs()
                for sub in subs:
                    logger.info('deleting sub %s', sub.get('id'))
                    await self.http_reqs.delete_event_sub(eventsub_id=sub.get('id'))

                await self.create_sub(session_id=self.session_id)

                logger.info('ready to read subs events ')

                async for mssg in self._socket:
                    logger.info('got new message: %s', mssg.data)
                    try:
                        event = typing.cast(
                            'Mapping[str, str]',
                            EventSchema().load(json.loads(mssg.data)),
                        )
                    except Exception as e:  # noqa: BLE001
                        logger.warning('cant load event %s', mssg.data, exc_info=e)
                        continue
                    await self.process_event(event)


class ChannelBotClient(BotClient):
    @typing.override
    async def create_sub(self, session_id: str) -> None:
        logger.info('channel_subsribe %s', self.broadcaster_user_id)
        await self.http_reqs.create_sub_channel_subscribe(
            session_id=session_id, broadcaster_user_id=self.broadcaster_user_id
        )
        await self.http_reqs.create_sub_channel_raid(
            session_id=session_id, broadcaster_user_id=self.broadcaster_user_id
        )
        await self.http_reqs.create_sub_custom_reward_redemption_add(
            session_id=session_id, broadcaster_user_id=self.broadcaster_user_id
        )


class SenderBotClient(BotClient):
    @typing.override
    async def create_sub(self, session_id: str) -> None:
        # we dont need subs here
        pass

    async def send_message(self, message: str):
        await self.http_reqs.send_message(
            self.broadcaster_user_id, self.user_id, message
        )
