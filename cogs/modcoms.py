import asyncio
import json
from string import Template
from pathlib import Path

import discord
from discord.ext import commands

import global_settings as gvars
from FkPyramids import load_file, send_mention, get_followers
from twitch_bot import twitch_bot


class Mod_Commands:
    """Can only be used by FkPyramids moderators"""

    def __init__(self, bot):
        self.bot = bot
        self.types = {"playing": 1, "listening": 2, "watching": 3}
        self.autoupdate = load_file("autoupdate10k.json")

    def __global_check(self, ctx):
        return ctx.message.author.id in gvars.mods or commands.is_owner()

    def dump(self, filename, txt):
        path = Path.cwd().joinpath("config", filename)
        with path.open(mode="w") as f:
            json.dump(txt, f, indent=2)

    @commands.command()
    async def pyramid(self, ctx, length: int, *, message: str):
        """Creates pyramids."""
        message += " "
        for i in [length - abs(i) for i in range(-length + 1, length)]:
            await ctx.send(message * i)

    @commands.command()
    async def delmsg(self, ctx, n: int):
        """
        Deletes messages.

        Requires "Manage Messages" permission
        """
        async for m in ctx.message.channel.history(limit=n):
            try:
                await m.delete()
            except discord.errors.Forbidden:
                print("Insufficient permissions")

    @commands.command()
    async def addcom(self, ctx, command: str, *, output: str):
        """Adds a command."""
        gvars.commands[command] = output
        self.dump("commands.json", gvars.commands)

        await send_mention(ctx, f'Added command "{command}"')

    @commands.command()
    async def delcom(self, ctx, command: str):
        """
        Deletes command.
        
        Only works for user-added commands.
        """
        if command in gvars.commands:
            del gvars.commands[command]
            self.dump("commands.json", gvars.commands)

            await send_mention(ctx, f'Removed command "{command}"')
        else:
            await send_mention(ctx, f'Command "{command}" doesn\'t exist')

    @commands.command()
    async def addincom(self, ctx, in_com: str, *, output: str):
        """Adds in_command."""
        gvars.incoms[in_com] = output
        self.dump("incoms.json", gvars.incoms)

        await send_mention(ctx, f'Added in_command "{in_com}"')

    @commands.command()
    async def delincom(self, ctx, in_com: str):
        """Deletes in_command."""
        if in_com in gvars.incoms:
            del gvars.incoms[in_command]
            self.dump("incoms.json", gvars.incos)

            await send_mention(ctx, f'Removed in_command "{in_com}"')
        else:
            await send_mention(ctx, f'In_command "{in_com}" doesn\'t exist')

    @commands.command()
    async def addmodcom(self, ctx, command: str, *, output: str):
        """Add mod commmand."""
        gvars.mod_coms[command] = output
        self.dump("modcoms.json", gvars.mod_coms)

        await channel.send(f'{mention} Added mod command "{command}"')

    @commands.command()
    async def delmodcom(self, ctx, command: str):
        """
        Delete mod command.
        
        (Only works for user-added mod commands)
        """
        if modcom in gvars.mod_coms:
            del gvars.mod_coms[command]
            self.dump("modcoms.json", gvars.mod_coms)

            await send_mention(ctx, f'Deleted mod command "{command}"')
        else:
            send_mention(ctx, f'Mod command "{command}" doesn\'t exist')

    @commands.command()
    async def delroles(self, ctx):
        """
        Delete all unused roles in server.

        Requires "Manage Roles" permission.
        """
        unused_roles = filter(lambda r: not r.members, ctx.message.guild.roles)
        for r in list(unused_roles):
            await r.delete()
            await ctx.send(f'Deleted role "{r.name}".')

        await ctx.send("Deleted unused roles.")

    @commands.command()
    async def react(self, ctx, n: int, em: str):
        """
        Add reaction to last [n] messages in channel.
        
        Takes emoji as ID or string
        """
        if em.isdigit():
            # Get emoji by ID
            em = discord.utils.get(bot.emojis(), id=int(em))

            if em:
                async for i in ctx.history(limit=n):
                    await i.add_reaction(em)
            else:
                await send_mention(ctx, "Could not find emote")
        else:
            # Get emoji directly using string
            try:
                async for i in ctx.history(limit=n):
                    await i.add_reaction(em[2:-1])
            except (discord.errors.NotFound, discord.errors.InvalidArgument):
                await send_mention(ctx, "Usage: `!fpreact [n] [emote]`")
            except discord.errors.Forbidden:
                await send_mention(ctx, "Could not react to message.")

    @commands.command()
    async def whitelist(self, ctx, user: int):
        """Whitelist user from pyramid blocking."""
        gvars.no_block_users.append(user)

    @commands.command()
    async def blacklist(self, ctx, user: int):
        """Remove user from pyramid blocking whitelist."""
        if user in no_block_users:
            gvars.no_block_users.remove(user)
        else:
            await send_mention(ctx, f"{user} is not whitelisted")

    @commands.command()
    async def s(self, ctx, n: int, message: str):
        """Send message [n] amount of times in a row."""
        for i in range(n):
            await ctx.send(message)

    @commands.command()
    async def status(self, ctx, activity_type: str, *, name: str):
        """
        Change activity status of bot.

        Takes activity_type as integer or string
        1: playing, 2: listening, 3: watching

        Examples:
          fp!status playing games
          fp!status watching ninten866
          fp!status 1 KH2FMHD PS4 Pro SSD Critical Mode Lvl 1 any%
        """
        try:
            activity_type = int(activity_type)
        except ValueError:
            if activity_type in self.types:
                activity_type = self.types[activity_type]
            else:
                return await send_mention(ctx, "Invalid type")

        await bot.change_presence(
            activity=discord.Activity(name=name, type=activity_type)
        )
        await send_mention(ctx, f'Set activity to "{name}"')

    @commands.command()
    async def whenis10k(self, ctx, channel: str, *, msg: str=None):
        """
        Returns how many followers until 10k.

        Takes a Twitch channel and looks up how far they are from 10k folllowers.
        Optionally can take a message format, formatted with ${left}.


        Examples:
          fp!whenis10k ninten866:
            Gets how far ninten866 is from 10k, in format `${left} until 10k`.

          fp!whenis10k ninten866 Only ${left} left until 10k Pog:
            Same as above, but in format `Only ${left} left until 10k Pog`.
        """
        followers = await twitch_bot.get_followers(channel)

        try:
            followers = int(followers)
        except ValueError:
            return await ctx.send(followers)

        left = 10000 - followers

        if msg:
            return await ctx.send(Template(msg).substitute(left=left))

        await ctx.send(f"{left} until 10k")

    @commands.command()
    async def update10k(self, ctx, channel: str, ID: int, *, msg: str=None):
        """Update 10k message by ID."""
        followers = await self.get_followers(channel)

        try:
            followers = int(followers)
        except ValueError:
            return await ctx.send(followers)

        left = 10000 - followers
        message = await ctx.get_message(ID)

        if msg:
            return await message.edit(
                    content=Template(msg).substitute(left=left)
                )
        await message.edit(content=f"{left} until 10k")

    @commands.command()
    async def autoupdate10k(self, ctx, channel, chan_id, msg_id, *, msg=None):
        """Automatically update 10k message by ID."""
        try:
            chan_id = int(chan_id)
            msg_id = int(msg_id)
        except ValueError:
            return await ctx.send("Invalid input")

        chan = self.bot.get_channel(chan_id)

        if not chan:
            return await ctx.send("Could not find discord channel")

        message = await chan.get_message(msg_id)
        followers = await get_followers(channel)

        try:
            followers = int(followers)
        except ValueError:
            return await ctx.send(followers)

        if chan_id in self.autoupdate:
            self.autoupdate[chan_id][msg_id] = (channel, msg)
        else:
            self.autoupdate[chan_id] = {msg_id: (channel, msg)}

        self.dump("autoupdate10k.json", self.autoupdate)
        await ctx.send(
            f"Updating message with ID {msg_id} with {msg} every 5 minutes"
        )

        while True:
            followers = await get_followers(channel)
            left = 10000 - followers

            if msg:
                await message.edit(content=Template(msg).substitute(left=left))
            else:
                await message.edit(content=f"{left} until 10k")

            await asyncio.sleep(300)

    @commands.command()
    async def delautoupdate(self, ctx, msg_ID, channel_ID=None):
        """Remove message from 10k auto update."""
        if not channel_ID:
            channel_ID = ctx.channel.id

        del self.autoupdate[channel_ID][msg_ID]

        if not self.autoupdate[channel_ID]:
            del self.autoupdate[channel_ID]

        self.dump("autoupdate10k.json", self.autoupdate)
        await ctx.send(
            "Removed message {} in channel {} from auto update".format(
                msg_ID, channel_ID
            )
        )


def setup(bot):
    bot.add_cog(Mod_Commands(bot))
