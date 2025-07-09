import typing
import time
from dataclasses import dataclass, fields as dfields, field


class Magic:
    def get_attr(self, name: str) -> str:
        if name.endswith('token') or 'secret' in name.lower():
            v = getattr(self, name)
            return f'secret: #### {v[-4:]}'
        return getattr(self, name)

    @typing.override
    def __str__(self):
        # Manually build the default dataclass output
        field_values = [f'{f.name}={self.get_attr(f.name)!r}' for f in dfields(self)]  # pyright: ignore[reportArgumentType]
        return f'{self.__class__.__name__}({", ".join(field_values)})'

    @typing.override
    def __repr__(self):
        # Manually build the default dataclass output
        field_values = [f'{f.name}={self.get_attr(f.name)!r}' for f in dfields(self)]  # pyright: ignore[reportArgumentType]
        return f'{self.__class__.__name__}({", ".join(field_values)})'


@dataclass
class TokenResponse(Magic):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str = ''
    last_updated: float = field(default_factory=lambda: time.time())
