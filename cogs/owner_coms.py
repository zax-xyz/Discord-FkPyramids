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
import datetime
import json
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands

import global_settings as gvars


async def send_mention(ctx, message):
    await ctx.send(ctx.author.mention + " " + message)


async def haste(content):
    async with aiohttp.ClientSession() as session:
        async with session.post("https://hastebin.com/documents",
                                data=content.encode('utf-8')) as post:
            post = await post.json()
            return "https://hastebin.com/{}".format(post['key'])


class Owner(commands.Cog):

    """Can only be used by FkPyramids owner (Zax#9935)"""

    def __init__(self, bot):
        self.bot = bot

    def __local_check(self, ctx):
        return ctx.author.id in (self.bot.owner_id, 354248004154294283)

    def dump(self, filename, txt):
        path = Path.cwd().joinpath("config", filename)
        with path.open(mode="w") as f:
            json.dump(txt, f, indent=2)

    @commands.command()
    async def send(self, ctx, channel_id: int, *, message: str):
        """Sends message to channel by ID."""
        await self.bot.get_channel(channel_id).send(message)

    @commands.group(aliases=["mod"])
    async def users(self, ctx):
        """Manage moderators."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @users.command(name="add")
    async def adduser(self, ctx, user: str):
        """Add user to moderator list."""
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = self.bot.get_user(user).mention
        gvars.mods.append(user)
        self.dump("users.json", gvars.mods)

        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Added user to moderators",
            description=f"Added {user_mention} to moderators."
        ))

    @users.command(name="delete")
    async def deluser(self, ctx, user: str):
        """Remove user from moderator list."""
        if ctx.message.mentions:
            user = ctx.message.mentions[0].id

        user_mention = self.bot.get_user(user).mention

        if user in gvars.mods:
            gvars.mods.remove(user)
            self.dump("users.json", gvars.mods)

            await ctx.send(embed=self.bot.create_embed(
                ctx,
                title="Removed user from moderators",
                description=f"Removed {user_mention} from moderators."
            ))
        else:
            await ctx.send(embed=self.bot.create_embed(
                ctx,
                title="User not in moderators",
                description=f"{user_mention} is not a moderator."
            ))

    @commands.command()
    async def clear(self, ctx):
        """
        Clear internal bot cache.

        Breaks bot.
        """
        await asyncio.sleep(0.5)
        self.bot.clear()
        await ctx.send('Internal cache cleared.')

    @commands.command(aliases=["exit", "close"])
    async def shutdown(self, ctx):
        """Shutdown bot."""
        await ctx.send('Shutting down client.')
        await self.bot.close()

    @commands.group(aliases=["extensions"])
    async def extension(self, ctx):
        """Manage extensions."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Invalid command passed",
                description="An invalid subcommand was passed."
            ))

    @extension.command()
    async def load(self, ctx, ext):
        """Load a cog/extension"""
        self.bot.load_extension(ext)
        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Loaded extension",
            description=f"Extension `{ext}` loaded."
        ))

    @extension.command()
    async def unload(self, ctx, ext):
        """Unload a cog/extension"""
        self.bot.unload_extension(ext)
        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Unloaded extension",
            description=f"Extension `{ext}` unloaded."
        ))

    @extension.command()
    async def reload(self, ctx, ext):
        """Reload a cog/extension"""
        self.bot.reload_extension(ext)
        await ctx.send(embed=self.bot.create_embed(
            ctx,
            title="Reloaded extension",
            description=f"Extension `{ext}` reloaded."
        ))

    @commands.command(aliases=["evaluate"])
    async def eval(self, ctx, block: int, *, code):
        """Evaluate code."""
        env = {
            'ctx': ctx,
            'bot': self.bot,
        }

        env.update(globals())
        out = eval(code, env)

        if type(out) in (list, dict) and len(out) >= 10:
            out = json.dumps(out, indent=2)
        else:
            out = str(out)

        if len(out) >= 1000:
            link = await haste(out)
            return await ctx.send(link)

        if block:
            await ctx.send(f"```\n{out}\n```")
        else:
            await ctx.send(out)

    @commands.command(aliases=["execute"])
    async def exec(self, ctx, *, code):
        """Execute code."""
        env = {
            'ctx': ctx,
            'bot': self.bot,
        }

        env.update(globals())
        exec(code, env)

    @commands.command(hidden=True)
    async def status_history(self, ctx, user):
        """Get status history of a user in bot cache."""
        try:
            user = int(user)
        except ValueError:
            user = ctx.message.mentions[0]
        else:
            user = self.bot.get_user(user)

        name = user.name
        ID = user.id

        try:
            statuses = self.bot.statuses[ID]
        except KeyError:
            return await ctx.send(embed=self.bot.error_embed(
                ctx,
                title="Error in command `status_history`",
                description="User has no status history"
            ))

        embed = discord.Embed(
            title=f"{name} status history",
            timestamp=datetime.datetime.utcnow()
        )

        for d in statuses:
            d_nice = "{}:{}:{} {}/{}/{}".format(d.hour, d.minute, d.second,
                                                d.day, d.month, d.year)
            embed.add_field(name=d_nice, value=statuses[d], inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
