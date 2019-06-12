"""
Copyright (C) 2018  Zaxutic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import asyncio
import json
from pathlib import Path

import discord
from discord.ext import commands

import global_settings as gvars
from FkPyramids import load_file, send_mention


class Mod(commands.Cog):

    """Can only be used by FkPyramids moderators"""

    def __init__(self, bot):
        self.bot = bot
        self.types = {"playing": 1, "listening": 2, "watching": 3}
        self.autoupdate = load_file("autoupdate10k.json")

    def __local_check(self, ctx):
        return self.bot._is_mod(ctx.author.id)

    def dump(self, filename, txt):
        path = Path.cwd().joinpath("config", filename)
        with path.open(mode="w") as f:
            json.dump(txt, f, indent=2)

    async def com_update(self, ctx, txt, com):
        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title=txt,
            description=f"{txt} `{com}`."
        ))

    async def com_not_found(self, ctx, com_type, com):
        await ctx.send(embed=self.bot.error_embed(
            ctx,
            title=f"{com_type} not found",
            description=f"{com_type} `{com}` doesn't seem to exist."
        ))

    @commands.command(aliases=["py"])
    async def pyramid(self, ctx, length: int, *, message: str):
        """
        Creates pyramids.

        Examples:
          pyramid 3 peepoS
            Returns:
              peepoS
              peepoS peepoS
              peepoS peepoS peepoS
              peepoS peepoS
              peepoS

          pyramid 2 yikes
            Returns:
              yikes
              yikes yikes
              yikes

        Note:
          Discord's rate limits only allow bots to send 5 messages per 5
          seconds.
        """
        message += " "
        lst = [length - abs(i) for i in range(-length + 1, length)]
        for i in lst:
            asyncio.ensure_future(ctx.send(message * i))

    @commands.command()
    async def delmsg(self, ctx, n: int):
        """
        Deletes <n> messages.

        Requires "Manage Messages" permission
        """
        async for m in ctx.message.channel.history(limit=n):
            try:
                await m.delete()
            except discord.errors.Forbidden:
                print("Insufficient permissions")

    @commands.group(aliases=["com"])
    async def command(self, ctx):
        """Manage custom commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @command.command(name="add")
    async def addcom(self, ctx, command: str, *, output: str):
        """Adds a command."""
        gvars.commands[command] = output
        self.dump("commands.json", gvars.commands)

        await self.com_update(ctx, "Added command", command)

    @command.command(name="delete")
    async def delcom(self, ctx, command: str):
        """
        Deletes command.

        Only works for user-added commands.
        """
        try:
            del gvars.commands[command]
        except KeyError:
            await self.com_not_found(ctx, "Command", command)
        else:
            self.dump("commands.json", gvars.commands)

            await self.com_update(ctx, "Removed command", command)

    @command.command(name="edit")
    async def editcom(self, ctx, command: str, *, output: str):
        """Edits command."""
        gvars.commands[command] = output
        self.dump("commands.json", gvars.commands)

        await self.com_update(ctx, "Edited command", command)

    @command.command(name="rename")
    async def renamecom(self, ctx, old: str, new: str):
        """Renames command."""
        try:
            gvars.commands[new] = gvars.commands[old]
        except KeyError:
            await self.com_not_found(ctx, "Command", old)
        else:
            del gvars.commands[old]
            self.dump("commands.json", gvars.commands)

            await self.com_update(ctx, "Renamed command", old)

    @commands.group()
    async def incom(self, ctx):
        """Manage in_commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @incom.command(name="add")
    async def addincom(self, ctx, in_com: str, *, output: str):
        """Adds in_command."""
        gvars.incoms[in_com] = output
        self.dump("incoms.json", gvars.incoms)

        await self.com_update(ctx, "Added in_command", in_com)

    @incom.command(name="delete")
    async def delincom(self, ctx, in_com: str):
        """Deletes in_command."""
        try:
            del gvars.incoms[in_com]
        except KeyError:
            await self.com_not_found(ctx, "In_command", in_com)
        else:
            self.dump("incoms.json", gvars.incoms)

            await self.com_update(ctx, "Removed in_command", in_com)

    @incom.command(name="edit")
    async def editincom(self, ctx, in_com: str, *, output: str):
        """Edits in_command."""
        gvars.incoms[in_com] = output
        self.dump("incoms.json", gvars.incoms)

        await self.com_update(ctx, "Edited in_command", in_com)

    @incom.command(name="rename")
    async def rename_incom(self, ctx, old: str, new: str):
        """Renames in_command."""
        try:
            gvars.incoms[new] = gvars.incoms[old]
        except KeyError:
            await self.com_not_found(ctx, "In_command", old)
        else:
            del gvars.incoms[old]
            self.dump("incoms.json", gvars.incoms)

            await self.com_update(ctx, "Renamed in_command", old)

    @commands.group()
    async def modcom(self, ctx):
        """Manage mod commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @modcom.command(name="add")
    async def addmodcom(self, ctx, command: str, *, output: str):
        """Adds mod commmand."""
        gvars.mod_coms[command] = output
        self.dump("modcoms.json", gvars.mod_coms)

        await self.com_update(ctx, "Added mod command", command)

    @modcom.command(name="delete")
    async def delmodcom(self, ctx, command: str):
        """
        Deletes mod command.

        (Only works for user-added mod commands)
        """
        try:
            del gvars.mod_coms[command]
        except KeyError:
            await self.com_not_found(ctx, "Mod command", command)
        else:
            self.dump("modcoms.json", gvars.mod_coms)

            await self.com_update(ctx, "Deleted mod command", command)

    @modcom.command(name="edit")
    async def editmodcom(self, ctx, command: str, *, output: str):
        """Edit mod command."""
        gvars.mod_coms[command] = output
        self.dump("modcoms.json", gvars.mod_coms)

        await self.com_update(ctx, "Edited mod command", command)

    @modcom.command(name="rename")
    async def rename_modcom(self, ctx, old: str, new: str):
        """Renames in_command."""
        try:
            gvars.mod_coms[new] = gvars.mod_coms[old]
        except KeyError:
            await self.com_not_found(ctx, "Mod command", old)
        else:
            del gvars.mod_coms[old]
            self.dump("modcoms.json", gvars.mod_coms)

            await self.com_update(ctx, "Renamed mod command", old)

    @commands.command()
    async def delroles(self, ctx):
        """
        Deletes all unused roles in server.

        Requires "Manage Roles" permission.
        """
        unused_roles = filter(lambda r: not r.members, ctx.message.guild.roles)
        for r in list(unused_roles):
            await r.delete()
            await ctx.send(f'Deleted role "{r.name}".')

        await ctx.send("Deleted unused roles.")

    @commands.command()
    async def react(self, ctx, n: int, emoji: str):
        """
        Add reaction to last <n> messages in channel.

        Takes emoji as ID, directly, or as the name.

        Examples:
          react 10 peepoS
          react 10 458944535578411010
          react 10 🤔
          react 10 <:thinkHang:458944535578411010>
        """
        if emoji.isdigit():
            # Get emoji by ID
            emoji = discord.utils.get(self.bot.emojis, id=int(emoji))

            if emoji:
                async for i in ctx.history(limit=n):
                    await i.add_reaction(emoji)
            else:
                await send_mention(ctx, "Could not find emote")
        else:
            # Get emoji directly using string
            if emoji[0] == "<" and emoji[-1] == ">":
                emoji = emoji[2:-1]
            else:
                emoji_get = discord.utils.get(self.bot.emojis, name=emoji)
                if emoji_get:
                    emoji = emoji_get
                else:
                    emoji = emoji

            async for i in ctx.history(limit=n):
                await i.add_reaction(emoji)

    @commands.group()
    async def whitelist(self, ctx):
        """Manage pyramid blocking whitelist."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @whitelist.command(name="add")
    async def add_whitelist(self, ctx, user: int):
        """Whitelist user from pyramid blocking."""
        gvars.no_block_users.append(user)

    @whitelist.command(name="remove")
    async def del_blacklist(self, ctx, user: int):
        """Remove user from pyramid blocking whitelist."""
        if user in gvars.no_block_users:
            gvars.no_block_users.remove(user)
        else:
            await send_mention(ctx, f"{user} is not whitelisted")

    @commands.command()
    async def s(self, ctx, n: int, *, message: str):
        """
        Send message <n> amount of times in a row.

        Note:
          Discord's rate limits only allow bots to send 5 messages per 5
          seconds.
        """
        for i in range(n):
            await ctx.send(message)

    @commands.command()
    async def sayd(self, ctx, *, message: str):
        """
        Sends a message then deletes the message that invoked the command.
        """
        await ctx.message.delete()
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

        await self.bot.change_presence(
            activity=discord.Activity(name=name, type=activity_type)
        )
        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Set activity",
            description=f'Set activity to "{name}"'
        ))


def setup(bot):
    bot.add_cog(Mod(bot))
