from twitchio import commands

from .config import auth


bot = commands.TwitchBot(prefix=[], api_token=auth.api_token,
                         client_id=auth.client_id)

async def get_followers(channel):
    followers = await bot.get_followers(channel)
    return followers['total']
