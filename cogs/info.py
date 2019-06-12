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

from datetime import datetime
from pkg_resources import get_distribution

import discord
from discord.ext import commands

import global_settings as gvars
from config import config


def plural(num):
    return "s" if num != 1 else ""


class Info(commands.Cog):

    """Bot info-related commands"""

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @commands.command(name="commands")
    async def _commands(self, ctx):
        """Displays available user-added commands."""

        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Commands",
            description=", ".join(f"`{x}`" for x in sorted(gvars.commands))
                        + f" (See `{config.prefix}help` for more)"
        ))

    @commands.command()
    async def mods(self, ctx):
        """
        Displays moderators for FkPyramids.

        Moderators get access to additional commands
        """
        mods_men = [self.bot._get_user(x) for x in gvars.mods]
        await ctx.send(embed=self.bot.create_embed(
            ctx, title="Mods", description=", ".join(str(x) for x in mods_men)
        ))

    @commands.command()
    async def incoms(self, ctx):
        """
        Displays available in_commands.

        In_commands are triggered by a keyword being anywhere in the message.
        """
        await ctx.send(embed=self.bot.create_embed(
            ctx, title="In_commands",
            description=", ".join(sorted(gvars.incoms))
        ))

    @commands.command()
    async def modcoms(self, ctx):
        """Displays available moderator commands."""
        await ctx.send(embed=self.bot.create_embed(
            ctx, title="Mod_commands",
            description=", ".join(sorted(gvars.mod_coms))
        ))

    @commands.command(aliases=["inv"])
    async def invite(self, ctx):
        """
        Invite bot to server.

        Gets link to invite bot to your own server
        """
        _id = self.bot.user.id
        url = ("https://discordapp.com/oauth2/authorize?client_id="
               f"{_id}&scope=bot")

        await ctx.send(embed=self.bot.create_embed(
            ctx, description=f"Invite me to your server [**here**]({url})"))

    def _uptime(self):
        time_now = datetime.utcnow()
        time_delta = time_now - self.bot.start_time
        d = datetime(1, 1, 1) + time_delta

        days = f"{d.day - 1} day{plural(d.day - 1)}"
        hours = f"{d.hour} hour{plural(d.hour)}"
        minutes = f"{d.minute} minute{plural(d.minute)}"
        seconds = f"{d.second} second{plural(d.second)}"

        return f"{days}, {hours}, {minutes}, {seconds}"

    @commands.command()
    async def uptime(self, ctx):
        """Displays bot's current uptime."""
        embed = discord.Embed(timestamp=self.bot.start_time,
                              title="Uptime",
                              description=self._uptime())
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """Displays current information about the bot."""
        bot = self.bot
        version = str(get_distribution("discord.py")).split("+")[0]

        embed = discord.Embed(timestamp=bot.start_time)
        embed.set_author(name=bot.owner, icon_url=bot.owner.avatar_url)
        embed.add_field(name="Uptime", value=self._uptime())
        embed.add_field(name="Latency", value=f"~{bot.latency} seconds")
        embed.add_field(name="Users", value=len(bot.users))
        embed.add_field(name="Servers", value=len(bot.guilds))
        embed.add_field(name="Channels",
                        value=sum(1 for _ in bot.get_all_channels()))
        embed.add_field(name="Emoji", value=len(bot.emojis))
        embed.add_field(name="Memory Usage", value=bot.memory_usage)
        embed.add_field(name="CPU Usage", value=bot.cpu_usage)
        embed.set_footer(text=f"Made with {version}",
                         icon_url="https://zaxutic.ddns.net/python.png")

        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        """Displays information regarding bot and its creation."""
        embed = discord.Embed(
            title="About",
            description="This is a bot made by <@135678905028706304>. The "
                        "original purpose of was to block pyramids, however "
                        "the focus of the bot has shifted away from that and "
                        "has now had several unrelated functionalities built "
                        "into it. Yes, I know the name of the bot doesn't "
                        "really make sense now that it is no longer focused on"
                        " that :)",
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.bot.owner, icon_url=ctx.bot.owner.avatar_url)
        embed.set_footer(text=f"See {ctx.prefix}help for available commands")
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx, *, com=None):
        """Displays this message"""
        if not com:
            prefix = ctx.prefix
            embed = discord.Embed(
                title="**Commands**",
                description="This doesn't include everything. See "
                            f"{prefix}commands for dynamically added user "
                            "commands.",
                timestamp=datetime.utcnow()
            )
            embed.set_footer(
                text=f"Type {prefix}help command for more information on a "
                     f"command. You can also type {prefix}help category for"
                     "more information on a category."
            )

            for cog in sorted(self.bot.cogs):
                coms = sorted(self.bot.get_cog(cog).get_commands(), key=str)
                if not coms:
                    continue

                value = ", ".join([f"`{c}`" for c in coms if not c.hidden and
                                   await c.can_run(ctx)])
                embed.add_field(name=cog, value=value, inline=False)
            await ctx.send(embed=embed)
        elif com in self.bot.cogs:
            cog = self.bot.get_cog(com)
            embed = discord.Embed(
                title=f"**{com}**",
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=cog.description)

            for command in cog.get_commands():
                if not command.hidden and await command.can_run(ctx):
                    embed.add_field(
                        name=f"{command} {command.signature}",
                        value=command.short_doc,
                        inline=False
                    )

            await ctx.send(embed=embed)
        else:
            command = self.bot.get_command(com)
            if command is None:
                return await ctx.send("Command not found.")
            embed = discord.Embed(
                title=f"**{com}**",
                timestamp=datetime.utcnow()
            )
            aliases = command.aliases
            embed.add_field(name="Parent", value=command.parent)
            embed.add_field(
                name="Aliases", value=", ".join(aliases) if aliases else "None"
            )
            embed.add_field(name="Usage",
                            value=f"```\n{command.signature}```")

            try:
                subcommands = command.commands
            except AttributeError:
                embed.description = command.help
            else:
                embed.set_footer(text=command.help)
                for command in subcommands:
                    embed.add_field(
                        name=f"{command} {command.signature}",
                        value=command.help,
                        inline=False
                    )

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
