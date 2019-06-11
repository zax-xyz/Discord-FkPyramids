#!/usr/bin/env python
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
import importlib
import json
import logging
import psutil
import sys
import traceback
from pathlib import Path
from string import Template

import discord
from discord.ext import commands
from termcolor import colored

import global_settings as gvars
from config import config
from config.auth import token
from twitch_client import twitch_client


BOT_ACTIVITY = discord.Activity(
    name=config.activity_name,
    type=config.activity_type
)


def current_time():
    t = datetime.datetime.now()
    return colored(t.strftime("%Y-%m-%d %H:%M:%S"), "green")


def plural(num):
    return "s" if num != 1 else ""


def load_file(filename):
    path = Path.cwd().joinpath("config", filename)
    with path.open() as f:
        return json.load(f)


async def send_mention(ctx, message):
    await ctx.send(ctx.author.mention + " " + message)


async def get_followers(channel):
    try:
        followers = await twitch_client.get_followers(channel)
    except IndexError:
        return "Could not find followers for " + channel
    else:
        return followers


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=config.prefix, activity=BOT_ACTIVITY,
                         case_insensitive=True)
        self.process = psutil.Process()
        self.statuses = {}
        self.start_time = datetime.datetime.utcnow()

        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception:
                print(f"Failed to load extension {extension}.",
                      file=sys.stderr)
                traceback.print_exc()

    def _get_user(self, user):
        user_get = self.get_user(user)
        if user_get:
            return user_get.mention
        return user

    def _is_mod(self, user):
        try:
            user = int(user)
        except ValueError:
            user = user[2:-1]

        return user in gvars.mods + [self.owner.id]

    def reload_extension(self, ext):
        importlib.reload(importlib.import_module(ext))
        self.unload_extension(ext)
        self.load_extension(ext)

        return f"Reloaded extension `{ext}`."

    def create_embed(self, ctx, colour=0x6da1e7, title='', description=''):
        embed = discord.Embed(colour=discord.Colour(colour),
                              title=title,
                              description=description)
        embed.set_author(
            name=f"{ctx.author.name}",
            icon_url=ctx.author.avatar_url_as(static_format="png")
        )
        return embed

    def error_embed(self, ctx, title='', description=''):
        return self.create_embed(ctx, 0xe92323, title, description)

    async def autoupdate10k(self, channel, chan_id, msg_id, msg=None):
        try:
            chan_id = int(chan_id)
            msg_id = int(msg_id)
        except ValueError:
            return print(colored("Invalid input in autoupdate10k.json",
                                 "red", attrs=["bold"]))

        chan = self.get_channel(chan_id)

        if not chan:
            return print(f"Could not find discord channel {chan_id}")

        message = await chan.fetch_message(msg_id)
        followers = await get_followers(channel)

        try:
            followers = int(followers)
        except ValueError:
            return print(followers)

        print(
            f"Updating message with ID {msg_id} with `{msg}` every 5 minutes"
        )

        while True:
            followers = await get_followers(channel)
            left = 10000 - followers

            if msg:
                await message.edit(content=Template(msg).substitute(left=left))
            else:
                await message.edit(content=f"{left} until 10k")

            await asyncio.sleep(300)

    @property
    def uptime(self):
        time_now = datetime.datetime.utcnow()
        time_delta = time_now - self.start_time
        d = datetime.datetime(1, 1, 1) + time_delta

        days = f"{d.day - 1} day{plural(d.day - 1)}"
        hours = f"{d.hour} hour{plural(d.hour)}"
        minutes = f"{d.minute} minute{plural(d.minute)}"
        seconds = f"{d.second} second{plural(d.second)}"

        return f"{days}, {hours}, {minutes}, {seconds}"

    @property
    def memory_usage(self):
        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        return f"{memory_usage:.2f} MiB"

    @property
    def cpu_usage(self):
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        return f"{cpu_usage}%"


if __name__ == "__main__":
    gvars.init()

    logger = logging.getLogger("discord")
    handler = logging.FileHandler(
        filename="log/discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)

    startup_extensions = [
        "cogs.modcoms",
        "cogs.owner_coms",
        "cogs.info",
        "cogs.misc",
        "cogs.twitch",
        "extensions.events"
    ]

    gvars.commands = load_file("commands.json")
    gvars.incoms = load_file("incoms.json")
    gvars.mod_coms = load_file("modcoms.json")
    gvars.mods = load_file("users.json")

    bot = Bot()

    loop = asyncio.get_event_loop()
    bot.run(token)
