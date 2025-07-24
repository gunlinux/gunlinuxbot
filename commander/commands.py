import random
import typing
from retwitch.schemas import RetwitchEvent
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def auf(event: RetwitchEvent, **_: dict[str, typing.Any]) -> str | typing.Any:
    symbols = ['AWOO', 'AUF', 'gunlinAuf']
    symbols_len = random.randint(6, 12)  #  noqa: S311
    out = [random.choice(symbols) for _ in range(symbols_len)]  # noqa: S311
    auf_str = ' '.join(out)
    return f'@{event.user_name} Воистину {auf_str}'
