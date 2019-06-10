import twitchio

from .config import auth


bot = twitchio.Client(prefix=[], nick='', api_token=auth.api_token,
                      irc_token='', client_id=auth.client_id)


async def get_followers(channel):
    user = await bot.get_users(channel)
    followers = await bot.get_followers(user[0].id, count=True)
    return followers
