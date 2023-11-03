import os

from dotenv import load_dotenv
from twitchbot import Bot

load_dotenv()


access_token = os.environ.get('ACCESS_TOKEN', 'set_Dame_token')

bot = TwitchBot(access_token=access_token)
bot.run()
