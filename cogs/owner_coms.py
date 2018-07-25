import json

import discord
from discord.ext import commands


class Owner_Commands:
    """Can only be used by FkPyramids owner (Zax#9935)"""

    def __init__(self, bot):
        self.bot = bot

    def __global_chec(self, ctx):
        return commands.is_owner()

    @commands.command()
    async def send(self, ctx, channel_id: int, *, message: str):
        """Sends message to channel by ID."""
        await self.bot.get_channel(channel_id).send(message)

    @commands.command()
    async def adduser(self, ctx, user: str):
        """Add user to moderator list."""
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = bot.get_user(user).mention
        mods.append(user)
        with open("users.json", "w") as user_file:
            json.dump(mods)

        await send_mention(ctx, f'Added {user_mention} to moderators')

    @commands.command()
    async def deluser(self, ctx, user: str):
        """Remove user from moderator list."""
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = bot.get_user(user).mention

        if user in mods:
            mods.remove(user)
            with open('users.json', 'w') as user_file:
                json.dump(mods, user_file)

            await send_mention(ctx, f'Removed {user_mention} from moderators.')
        else:
            await send_mention(ctx, f'{user_mention} is not a moderator.')

    @commands.command()
    async def shutdown(self, ctx):
        """Shutdown bot."""
        await ctx.send('Shutting down client.')
        await bot.close()

    @commands.command()
    async def clear(self, ctx):
        """Clear internal bot cache."""
        bot.clear()
        await ctx.send('Internal cache cleared.')


def setup(bot):
    bot.add_cog(Owner_Commands(bot))
