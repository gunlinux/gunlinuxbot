import asyncio
import os
import logging
import sys
from retwitch.token import TokenManager
import dotenv

logger = logging.getLogger('twitchbot')


async def main():
    _ = dotenv.load_dotenv()
    client_id = os.getenv('CLIENT_ID', '')
    client_secret = os.getenv('CLIENT_SECRET', '')
    token_manager: TokenManager = TokenManager(
        client_id=client_id,
        client_secret=client_secret,
        token_file='channels_tokens.json',  # noqa: S106
    )
    token_manager.load_real_token()

    if len(sys.argv) == 1:
        url = token_manager.generate_code_url()
        print(url)
        sys.exit()

    if len(sys.argv) == 1 + 1:
        # только код -> сохраняем по умолчанию
        code = sys.argv[1]
        await token_manager.get_token_from_code(code=code)
        token_manager.save_real_token()
        return

    if len(sys.argv) == 1 + 1 + 1:
        # только код -> + channel_token
        code = sys.argv[1]
        file = sys.argv[2]
        await token_manager.get_token_from_code(code=code)
        token_manager.token_file = file
        token_manager.save_real_token()
        return


if __name__ == '__main__':
    asyncio.run(main())
