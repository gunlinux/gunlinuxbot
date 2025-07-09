import typing
import aiohttp
from collections.abc import Mapping
from http import HTTPStatus
from retwitch.token import TokenManager
from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitchbot')


EVENT_SUB = 'https://api.twitch.tv/helix/eventsub/subscriptions'


class HttpReqs:
    def __init__(self, token_manager: TokenManager, client_id: str) -> None:
        self.token_manager = token_manager
        self.client_id = client_id

    async def default_headers(
        self, **extra_headers: Mapping[str, str]
    ) -> Mapping[str, str]:
        token = await self.token_manager.get_access_token()
        if not token:
            raise ValueError('notoken_wtf')
        return typing.cast(
            'Mapping[str, str]',
            {
                'Authorization': f'Bearer {token}',
                'Client-Id': self.client_id,
                'Content-Type': 'application/json',
                **extra_headers,
            },
        )

    async def delete_event_sub(self, eventsub_id: str):
        async with aiohttp.ClientSession() as session:
            params = {
                'id': eventsub_id,
            }
            async with session.delete(
                EVENT_SUB, params=params, headers=await self.default_headers()
            ) as resp:
                if not resp.status == HTTPStatus.NO_CONTENT:
                    raise ValueError('wrong_status')

    async def get_subs(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                EVENT_SUB, headers=await self.default_headers()
            ) as resp:
                data = await resp.json()
                return data.get('data', [])

    async def create_sub_chat_message(
        self, session_id: str, broadcaster_user_id: str, user_id: str
    ):
        _type = 'channel.chat.message'
        async with aiohttp.ClientSession() as session:
            data = {
                'type': _type,
                'version': '1',
                'condition': {
                    'broadcaster_user_id': broadcaster_user_id,
                    'user_id': user_id,
                },
                'transport': {
                    'method': 'websocket',
                    'session_id': session_id,
                },
            }
            async with session.post(
                EVENT_SUB, headers=await self.default_headers(), json=data
            ) as resp:
                logger.info('%s %s', _type, resp.status)
                await resp.json()

    async def create_sub_channel_raid(self, session_id: str, broadcaster_user_id: str):
        _type = 'channel.raid'
        async with aiohttp.ClientSession() as session:
            if not self.token_manager:
                raise ValueError('not_token_manager')
            data = {
                'type': _type,
                'version': '1',
                'condition': {
                    'to_broadcaster_user_id': broadcaster_user_id,
                },
                'transport': {
                    'method': 'websocket',
                    'session_id': session_id,
                },
            }
            async with session.post(
                EVENT_SUB, headers=await self.default_headers(), json=data
            ) as resp:
                logger.info('%s %s', _type, resp.status)

    async def create_sub_channel_subscribe(
        self, session_id: str, broadcaster_user_id: str
    ):
        _type = 'channel.subscribe'
        async with aiohttp.ClientSession() as session:
            if not self.token_manager:
                raise ValueError('not_token_manager')
            data = {
                'type': _type,
                'version': '1',
                'condition': {
                    'broadcaster_user_id': broadcaster_user_id,
                },
                'transport': {
                    'method': 'websocket',
                    'session_id': session_id,
                },
            }
            async with session.post(
                EVENT_SUB, headers=await self.default_headers(), json=data
            ) as resp:
                logger.info('%s %s', _type, resp.status)

    async def create_sub_custom_reward_redemption_add(
        self, session_id: str, broadcaster_user_id: str
    ):
        _type = 'channel.channel_points_custom_reward_redemption.add'
        async with aiohttp.ClientSession() as session:
            if not self.token_manager:
                raise ValueError('not_token_manager')
            data = {
                'type': _type,
                'version': '1',
                'condition': {
                    'broadcaster_user_id': broadcaster_user_id,
                },
                'transport': {
                    'method': 'websocket',
                    'session_id': session_id,
                },
            }
            async with session.post(
                EVENT_SUB, headers=await self.default_headers(), json=data
            ) as resp:
                logger.info('%s %s', _type, resp.status)

    async def create_sub_channel_follow(
        self, session_id: str, broadcaster_user_id: str, user_id: str
    ):
        _type = 'channel.follow'
        async with aiohttp.ClientSession() as session:
            data = {
                'type': _type,
                'version': '2',
                'condition': {
                    'broadcaster_user_id': broadcaster_user_id,
                    'moderator_user_id': user_id,
                },
                'transport': {
                    'method': 'websocket',
                    'session_id': session_id,
                },
            }
            async with session.post(
                EVENT_SUB, headers=await self.default_headers(), json=data
            ) as resp:
                logger.info('%s %s', _type, resp.status)
