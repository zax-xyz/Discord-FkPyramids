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
import re
import sys
import time
import traceback

import discord
from termcolor import colored
from discord.ext import commands

import global_settings as gvars
from FkPyramids import BOT_ACTIVITY, current_time, load_file
from config import config


class Events(commands.Cog):

    """Events"""

    def __init__(self, bot):
        self.bot = bot
        self.Channels = {}
        self.incom_cooldown = 0
        self.com_cooldown = 0
        self.status_max_size = 20

    def update_status(self, member):
        activity = member.activity
        if not activity:
            return

        start = datetime.datetime.now()

        _id = member.id

        try:
            self.bot.statuses[_id][start] = activity.name
        except KeyError:
            self.bot.statuses[_id] = {start: activity.name}
        else:
            if len(self.bot.statuses[_id]) >= self.status_max_size:
                first_key = list(self.bot.statuses[_id].keys())[0]
                del self.bot.statuses[_id][first_key]

    async def update_statuses(self):
        for member in self.bot.get_all_members():
            self.update_status(member)

    def delete(self, chan):
        """Delete channel entry from dictionary"""
        if chan in self.Channels:
            del self.Channels[chan]

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            command = ctx.command.name
        except AttributeError:
            command = ctx.invoked_with
            parent = None
        else:
            parent = ctx.command.parent
        if parent:
            command = f"{parent.name} {command}"
        title = f"Error in command `{command}`"
        prefix = config.prefix
        if isinstance(error, commands.CommandNotFound):
            if prefix + command in gvars.commands:
                return
            return await ctx.send(embed=self.bot.error_embed(
                ctx, "Yikes.",
                "Yikes, that command wasn't found. "
                f"(See `{prefix}help` and `{prefix}commands`)"
            ))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title,
                f"Missing Required Argument (See `{prefix}help {command}`)"
            ))
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title,
                f"Bad Argument (See `{prefix}help {command}`)"
            ))
        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title,
                f"Too Many Arguments (See `{prefix}help {command}`)"
            ))
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title,
                "Command Not Found or Disabled. "
                f"(See `{prefix}help` and `{prefix}commands`.)"
            ))
        elif isinstance(error, commands.CommandOnCooldown):
            return
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title, "Not Owner."
            ))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title, f"Missing Permissions. ({error.missing_perms})"
            ))
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title, f"Bot Missing Permissions. ({error.missing_perms})"
            ))
        elif isinstance(error, commands.errors.CheckFailure):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title, "Not authorised to use command."
            ))
        elif isinstance(error, discord.errors.HTTPException):
            return await ctx.send(embed=self.bot.error_embed(
                ctx, title, "HTTP exception occured."
            ))
        elif isinstance(error, commands.CommandInvokeError):
            print(f"Ignoring exception in command {ctx.command}:",
                  file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__,
                                      file=sys.stderr)

            if ctx.author != self.bot.owner and ctx.invoked_with != "eval":
                out = ("Unknown error occurred in execution. "
                       " (Please notify bot creator (Zax#9935))")
            else:
                out = "Exception occured in execution."

            return await ctx.send(embed=self.bot.error_embed(ctx, title, out))

        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__,
                                  file=sys.stderr)
        await ctx.send(embed=self.bot.error_embed(
            f"Error in command `{command}`."))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(colored(f"Joined {guild.name}", "red", attrs=["bold"]))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        self.update_status(after)

    @commands.Cog.listener()
    async def on_message(self, message):
        user_id = message.author.id
        msg = message.content
        msg_parts = msg.split()
        channel = message.channel
        chan_id = channel.id
        name, disc = str(message.author).rsplit("#", 1)
        disc = "#" + disc

        mention_replace = (
            (message.mentions, lambda x: "@" + x.name),
            (message.channel_mentions, lambda x: "#" + x.name),
            (message.role_mentions, lambda x: "r@" + x.name)
        )

        sub_tup = (
            (r"<a?:\w+:\d+>", lambda x: f":{x.split(':')[1]}:"),
        )

        if msg:
            for tup in mention_replace:
                for i in tup[0]:
                    msg = re.sub(
                        i.mention,
                        lambda x: colored(tup[1](i), "cyan", attrs=["bold"]),
                        msg,
                    )

            for tup in sub_tup:
                msg = re.sub(
                    tup[0],
                    lambda x: colored(tup[1](x.group()), "cyan"),
                    msg
                )

        else:
            msg = colored(
                "Unable to display message (image, embed, etc)",
                "red",
                attrs=["bold"]
            )

        attachments = message.attachments
        if attachments:
            msg += " " + " ".join(colored(a.url, "cyan") for a in attachments)

        try:
            guild_name = message.guild.name
            channel_name = message.channel.name
        except AttributeError:
            guild_format = colored("{DM}", "red", attrs=["bold"])
        else:
            guild_format = colored(f"[{guild_name}:{channel_name}]",
                                   attrs=["bold"])

        if message.author != self.bot.user:
            color = "blue"
        else:
            color = "cyan"

        output = "{} {}  {}{}: {}".format(
            current_time(),
            guild_format,
            colored(name, color, attrs=["bold"]),
            colored(disc, "grey", attrs=["bold"]),
            msg
        )

        print(output)
        with open("log/message_log.txt", "a") as log_file:
            log_file.write(f"{output}\n")

        # Pyramid blocking
        if user_id not in gvars.no_block_users:
            if chan_id in self.Channels:
                if len(msg_parts) == 1:
                    if (len(msg_parts) == self.Channels[chan_id]["len"] - 1 and
                            msg == self.Channels[chan_id]["py"]):
                        # Completed 2-tier (baby) pyramid
                        await channel.send(message.author.mention +
                            " Baby pyramids don't count, you fucking degenerate.")

                    self.Channels[chan_id]["py"] = msg
                    self.Channels[chan_id]["len"] = 1
                elif len(msg_parts) == 1 + self.Channels[chan_id]["len"]:
                    self.Channels[chan_id]["len"] += 1

                    for part in msg_parts:
                        if part != self.Channels[chan_id]["py"]:
                            # Pyramid broken
                            del self.Channels[chan_id]
                            break
                    else:
                        if self.Channels[chan_id]["len"] == 3:
                            # Pyramid peaks
                            for i in [1, 2, 3, 2, 1]:
                                await channel.send("no " * i)

                            del self.Channels[chan_id]
                else:
                    # Pramid broken
                    del self.Channels[chan_id]
            elif len(msg_parts) == 1:
                # Pyramid start
                self.Channels[chan_id] = {"len": 1, "py": msg}
        elif chan_id in self.Channels:
            del self.Channels[chan_id]

        # Stop if user is the bot
        if color == "cyan" or not msg_parts:
            return

        # Custom commands
        com = msg_parts[0].lower()
        if time.time() - self.com_cooldown > 30:
            if user_id in gvars.mods and com in gvars.mod_coms:
                self.com_cooldown = time.time()
                return await channel.send(gvars.mod_coms[com])
            elif com in gvars.commands:
                self.com_cooldown = time.time()
                return await channel.send(gvars.commands[com])
            elif msg.lower() == "n":
                self.com_cooldown = time.time()
                return await channel.send("make")

        # In_commands
        if time.time() - self.incom_cooldown > 30:
            keys = (k for k in gvars.incoms if k in msg.lower())

            if keys:
                for key in keys:
                    await channel.send(gvars.incoms[key])
                self.incom_cooldown = time.time()

    @commands.Cog.listener()
    async def on_ready(self):
        print(current_time(), colored("Bot Online", "green", attrs=["bold"]))
        print(colored("Name:", "green", attrs=["bold"]), self.bot.user.name)
        print(colored("ID:", "green", attrs=["bold"]), self.bot.user.id)
        print(colored(f"In: {', '.join(g.name for g in self.bot.guilds)}",
                      "blue", attrs=["bold"]))

        await self.bot.change_presence(activity=BOT_ACTIVITY)

        bot_info = await self.bot.application_info()
        self.bot.owner_id = bot_info.owner.id
        self.bot.owner = self.bot.get_user(self.bot.owner_id)

        gvars.no_block_users = [self.bot.user.id, 135678905028706304]
        if self.bot.owner_id not in gvars.mods:
            gvars.mods.insert(0, self.bot.owner_id)

        autoupdate = load_file("autoupdate10k.json")

        for chan in autoupdate:
            messages = autoupdate[chan]
            for msg in messages:
                asyncio.ensure_future(self.bot.autoupdate10k(
                    messages[msg]["channel"], chan, msg, messages[msg]["msg"]
                ))

        asyncio.ensure_future(self.update_statuses())


def setup(bot):
    bot.add_cog(Events(bot))
