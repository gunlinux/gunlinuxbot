import logging
import typing
import json
import time
from pathlib import Path
from http import HTTPStatus

from urllib.parse import urlencode
from collections.abc import Mapping
from dataclasses import asdict

import aiohttp
from gunlinuxbot.utils import logger_setup
from retwitch.schemas import TokenResponseSchema

if typing.TYPE_CHECKING:
    from retwitch.models import TokenResponse


TOKEN_URL: str = 'https://id.twitch.tv/oauth2/token'  # noqa: S105
TWITCH_AUTH: str = 'https://id.twitch.tv/oauth2/authorize'
TOKEN_REVOKE: str = 'https://id.twitch.tv/oauth2/revoke'  # noqa: S105
REFRESH_TOKEN_DELTA: int = 6000
logger: logging.Logger = logger_setup(name='retwitch')


scopes = [
    'channel:bot',
    'channel:read:redemptions',
    'user:bot',
    'user:read:chat',
    'moderator:read:followers',
    'channel:read:subscriptions',
]


class TokenManager:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = 'https://gunlinux.ru/callback',
        token_file: str = 'tokens.json',  # noqa: S107
    ):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.token_file: str = token_file
        self.redirect_uri: str = redirect_uri
        self._token: TokenResponse | None = None

    def get_headers(self, **kwargs: dict[str, str]) -> Mapping[str, str]:
        return typing.cast(
            'Mapping[str, str]',
            {
                'Content-Type': 'application/x-www-form-urlencoded',
                **kwargs,
            },
        )

    async def _req_token(self, params: dict[str, typing.Any]):
        logger.info('start to req')
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=TOKEN_URL, headers=self.get_headers(), params=params
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    raise Exception(f'Dame {resp.status}')  # noqa: TRY003, TRY002, EM102
                self._token = typing.cast(
                    'TokenResponse', TokenResponseSchema().load(await resp.json())
                )
                return self._token

    async def get_access_token(self) -> str:
        if not self._token:
            raise ValueError('Dame')
        if (
            self._token.last_updated + self._token.expires_in - time.time()
        ) < REFRESH_TOKEN_DELTA:
            logger.warning('token close to die, time to refresh')
            await self.refresh_token()
            self.save_real_token()
        return self._token.access_token

    async def get_token_from_code(self, code: str) -> None:
        """
        получаем могучий токен
        """
        params = {
            'client_id': self.client_id,
            'code': code,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'scope': ' '.join(scopes),
            'redirect_uri': self.redirect_uri,
        }
        self._token = await self._req_token(params=params)

    async def refresh_token(self) -> None:
        if not self._token:
            raise ValueError('dame')
        logger.info('refreshing token %s', self._token)
        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self._token.refresh_token,
            'scope': ' '.join(scopes),
            'redirect_uri': self.redirect_uri,
        }
        self._token = await self._req_token(params=params)

    async def revoke(self, client_id: str) -> None:
        if not self._token:
            raise ValueError('Dame')

        params = {
            'client_id': client_id,
            'token': self._token.access_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=TOKEN_REVOKE, headers=self.get_headers(), params=params
            ) as resp:
                logger.info('revoke: %s', resp.status)

    def save_real_token(self) -> None:
        if not self._token:
            raise ValueError('Dame')
        path = Path(self.token_file)
        with path.open(mode='w') as f:
            json.dump(asdict(self._token), f)

    def load_real_token(self) -> None:
        path = Path(self.token_file)
        new_token: TokenResponse | None = None
        if path.exists():
            with path.open(mode='w') as f:
                logger.info('loading_token file from %s', self.token_file)
                new_token = typing.cast(
                    'TokenResponse', TokenResponseSchema().load(json.load(f))
                )
        if new_token:
            self._token = new_token

    def generate_code_url(self) -> str:
        base_url: str = TWITCH_AUTH
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'state': 'c3ab8aa609ea11e793ae92361f002671',
        }
        query_params = urlencode(params)
        return f'{base_url}?{query_params}'
