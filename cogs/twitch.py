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
from string import Template

from discord.ext import commands

from twitch_client import twitch_client


class Twitch(commands.Cog):

    """Tools related to Twitch."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def followers(self, ctx, channel: str):
        """Returns how many followers a Twitch channel has."""
        try:
            followers = await twitch_client.get_followers(channel)
        except IndexError:
            return await ctx.send(f"Could not get followers for {channel}")

        await ctx.send(followers)

    @commands.group(name="10k", invoke_without_command=True)
    async def _10k(self, ctx):
        """Set of 10k follower commands for Twitch."""
        await ctx.send(embed=self.bot.error_embed(
            ctx,
            title="Invalid command passed",
            description="An invalid subcommand was passed."
        ))

    @_10k.command(name="when")
    async def whenis10k(self, ctx, channel: str, *, msg: str=None):
        """
        Returns how far a Twitch channel is from 10k followers.

        Optionally can take a message format, formatted with ${left}.


        Examples:
          whenis10k ninten866:
            Gets how far ninten866 is from 10k, in format "${left} until 10k".

          whenis10k ninten866 Only ${left} left until 10k Pog:
            Same as above, but in format "Only ${left} left until 10k Pog".
        """
        try:
            followers = await twitch_client.get_followers(channel)
        except IndexError:
            return await ctx.send(f"Could not get followers for {channel}")

        left = 10000 - followers

        if msg:
            return await ctx.send(Template(msg).substitute(left=left))

        await ctx.send(f"{left} until 10k")

    @_10k.command(name="update")
    async def update10k(self, ctx, channel: str, id: int, *, msg: str=None):
        """Update 10k message by ID."""
        try:
            followers = await twitch_client.get_followers(channel)
        except IndexError:
            return await ctx.send(f"Could not get followers for {channel}")

        left = 10000 - followers
        message = await ctx.get_message(id)

        if msg:
            return await message.edit(
                content=Template(msg).substitute(left=left)
            )

        await message.edit(content=f"{left} until 10k")

    @_10k.command(name="autoupdate")
    async def autoupdate10k(self, ctx, channel, chan_id, msg_id, *, msg=None):
        """Automatically update 10k message by ID every 5 minutes."""
        try:
            chan_id = int(chan_id)
            msg_id = int(msg_id)
        except ValueError:
            return await ctx.send("Invalid input")

        chan = self.bot.get_channel(chan_id)

        if not chan:
            return await ctx.send("Could not find discord channel")

        message = await chan.get_message(msg_id)
        try:
            followers = await twitch_client.get_followers(channel)
        except IndexError:
            return await ctx.send(f"Could not get followers for {channel}")

        if chan_id in self.autoupdate:
            self.autoupdate[chan_id][msg_id] = {"channel": channel, "msg": msg}
        else:
            self.autoupdate[chan_id] = {
                msg_id: {"channel": channel, "msg": msg}
            }

        self.dump("autoupdate10k.json", self.autoupdate)
        await ctx.send(
            f"Updating message with ID {msg_id} with {msg} every 5 minutes"
        )

        while True:
            followers = await twitch_client.get_followers(channel)
            left = 10000 - followers

            if msg:
                await message.edit(content=Template(msg).substitute(left=left))
            else:
                await message.edit(content=f"{left} until 10k")

            await asyncio.sleep(300)

    @_10k.command(name="delete")
    async def delautoupdate(self, ctx, msg_id, channel_id=None):
        """Remove message from 10k auto update."""
        if not channel_id:
            channel_id = ctx.channel.id

        del self.autoupdate[channel_id][msg_id]

        if not self.autoupdate[channel_id]:
            del self.autoupdate[channel_id]

        self.dump("autoupdate10k.json", self.autoupdate)
        await ctx.send(
            "Removed message {} in channel {} from auto update".format(
                msg_id, channel_id
            )
        )


def setup(bot):
    bot.add_cog(Twitch(bot))
