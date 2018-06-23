import discord
from discord.ext import commands
from termcolor import colored
import json

class Owner_Commands:
    def __init__(self, bot):
        self.bot = bot


    def __global_chec(self, ctx):
        return commands.is_owner()


    @commands.command(brief="Sends message to channel by ID.")
    async def send(ctx, channel_id: int, *, message: str):
        await bot.get_channel(channel_id).send(message)


    @commands.command(brief="Add user to moderator list.")
    async def adduser(ctx, user: str):
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = bot.get_user(user).mention
        mods.append(user)

        with open("users.json", "w") as userFile:
            json.dump(mods)

        await send_mention(ctx, f'Added {user_mention} to moderators')


    @commands.command(brief="Remove user from moderator list.")
    async def deluser(ctx, user: str):
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = bot.get_user(user).mention

        if user in mods:
            mods.remove(user)
            with open('users.json', 'w') as userFile:
                json.dump(mods, userFile)

            await send_mention(ctx, f'Removed {user_mention} from moderators.')
        else:
            await send_mention(ctx, f'{user_mention} is not a moderator.')


    @commands.command(brief="Shutdown bot.")
    async def shutdown(ctx):
        await ctx.send('Shutting down client.')
        await bot.close()


    @commands.command(brief="Clear internal bot cache.")
    async def clear(ctx):
        bot.clear()
        await ctx.send('Internal cache cleared.')


def setup(bot):
    bot.add_cog(Owner_Commands(bot))
