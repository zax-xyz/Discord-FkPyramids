import asyncio
import datetime
import itertools
import json
import logging
import re
import sys
import time
import traceback
from string import Template
from pathlib import Path

import discord
from discord.ext import commands
try:
    from termcolor import colored
except ImportError:
    colored = lambda m, *args, **kwargs: m

import global_settings as gvars
from config import config
from config.auth import token
from twitch_bot import twitch_bot


bot = commands.Bot(
    command_prefix=config.prefix,
    activity=discord.Activity(
        name=config.activity_name,
        type=config.activity_type
    )
)

def current_time():
    t = datetime.datetime.now()
    return colored(t.strftime("%Y-%m-%d %H:%M:%S"), "green")


# Delete channel entry from dictionary
def delete(chan):
    if chan in Channels:
        del Channels[chan]


def get_user(user):
    user_get = bot.get_user(user)
    if user_get:
        return user_get.mention
    return user


def load_file(filename):
    path = Path.cwd().joinpath("config", filename)
    with path.open() as f:
        return json.load(f)


async def send_mention(ctx, message):
    await ctx.send(ctx.author.mention + " " + message)


def from_guild():
    def predicate(ctx):
        return ctx.message.guild.id == 311016926925029376
    return commands.check(predicate)


async def get_followers(channel):
    try:
        followers = await twitch_bot.get_followers(channel)
    except IndexError:
        return "Could not find followers for " + channel
    else:
        return followers


async def autoupdate10k(channel, chan_id, msg_id, msg=None):
    try:
        chan_id = int(chan_id)
        msg_id = int(msg_id)
    except ValueError:
        return print(colored("Invalid input in autoupdate10k.json",
                             "red", attrs=["bold"]))

    chan = bot.get_channel(chan_id)

    if not chan:
        return print(f"Could not find discord channel {chan_id}")

    message = await chan.get_message(msg_id)
    followers = await get_followers(channel)

    try:
        followers = int(followers)
    except ValueError:
        return print(followers)

    print(f"Updating message with ID {msg_id} with `{msg}` every 5 minutes")

    while True:
        followers = await get_followers(channel)
        left = 10000 - followers

        if msg:
            await message.edit(content=Template(msg).substitute(left=left))
        else:
            await message.edit(content=f"{left} until 10k")

        await asyncio.sleep(300)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(f"Command `{ctx.invoked_with}` not found.")

    print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__,
                              file=sys.stderr)


@bot.event
async def on_ready():
    print(current_time(), colored("Bot Online", "green", attrs=["bold"]))
    print(colored("Name:", "green", attrs=["bold"]), bot.user.name)
    print(colored("ID:", "green", attrs=["bold"]), bot.user.id)

    bot_info = await bot.application_info()
    local_vars["Owner"] = bot_info.owner.id

    gvars.no_block_users = [bot.user.id, 135678905028706304]
    if local_vars["Owner"] not in gvars.mods:
        gvars.mods.insert(0, local_vars["Owner"])

    autoupdate = load_file("autoupdate10k.json")

    for chan in autoupdate:
        messages = autoupdate[chan]
        for msg in messages:
            await autoupdate10k(
                messages[msg][0], chan, msg, messages[msg][1]
            )


@bot.event
async def on_guild_join(guild):
    print(colored(f"Joined {guild.name}", "red", attrs=["bold"]))


@bot.event
async def on_message(message):
    user_id = message.author.id
    msg = str(message.content)
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
        print("{} {}  {}{}: {}".format(
            current_time(),
            colored(f"[{message.guild.name}]", attrs=["bold"]),
            colored(
                name,
                "blue" if message.author != bot.user else "cyan",
                attrs=["bold"]),
            colored(disc, "grey", attrs=["bold"]),
            msg
        ))
    except AttributeError:
        print("{} {}  {}{}: {}".format(
            current_time(),
            colored("{DM}", "red", attrs=["bold"]),
            colored(
                name,
                "blue" if message.author != bot.user else "cyan",
                attrs=["bold"]),
            colored(disc, "grey", attrs=["bold"]),
            msg
        ))


    # Pyramid blocking
    if user_id not in gvars.no_block_users:
        if chan_id in Channels:
            if len(msg_parts) == 1:
                if (len(msg_parts) == Channels[chan_id]["len"] - 1 and
                        msg == Channels[chan_id]["py"]):
                    # Completed 2-tier (baby) pyramid
                    await send_mention(channel,
                        "Baby pyramids don't count, you fucking degenerate.")

                Channels[chan_id]["py"] = msg
                Channels[chan_id]["len"] = 1
            elif len(msg_parts) == 1 + Channels[chan_id]["len"]:
                Channels[chan_id]["len"] += 1

                for part in msg_parts:
                    if part != Channels[chan_id]["py"]:
                        # Pyramid broken
                        del Channels[chan_id]
                        break
                else:
                    if Channels[chan_id]["len"] == 3:
                        # Pyramid peaks
                        for i in [1, 2, 3, 2, 1]:
                            await channel.send("no " * i)

                        del Channels[chan_id]
            else:
                # Pramid broken
                del Channels[chan_id]
        elif len(msg_parts) == 1:
        # Pyramid start
            Channels[chan_id] = {"len": 1, "py": msg}
    elif chan_id in Channels:
        del Channels[chan_id]

    if user_id != bot.user.id and msg_parts:
        com = msg_parts[0]
        # Custom commands
        if user_id in gvars.mods:
            out = gvars.mod_coms.get(com, None)
            if out:
                return await channel.send(out)

        out = gvars.commands.get(com, None)
        if out:
            return await channel.send(gvars.commands[com])

        # In_commands
        if time.time() - local_vars["cooldown"] > 30:
            try:
                key = next(k for k in gvars.incoms if k in msg.lower())
                await channel.send(gvars.incoms[key])
                local_vars["cooldown"] = time.time()
            except StopIteration:
                pass

    await bot.process_commands(message)


@bot.command(name="commands")
async def _commands(ctx):
    """Displays available user-added commands."""
    desc = ", ".join(f"`{x}`" for x in gvars.commands)
    embed = discord.Embed(
        title="Commands",
        colour=discord.Colour(0x33baf9),
        description=f"{desc} (See `fp!help` for more)"
    )

    embed.set_author(name=f"{ctx.author.name}",
                     icon_url=ctx.author.avatar_url_as(static_format="png"))

    await ctx.send(embed=embed)


@bot.command()
async def mods(ctx):
    """
    Displays moderators for FkPyramids.
    
    Moderators get access to additional commands
    """
    mods_men = [get_user(x) for x in gvars.mods]
    await send_mention(ctx, "Mods: " + ", ".join(str(x) for x in mods_men))


@bot.command()
async def incoms(ctx):
    """
    Displays available in_commands.
    
    In_commands are triggered by a keyword being anywhere in the message.
    """
    await send_mention(ctx, "In_commands: " + ", ".join(gvars.incoms))


@bot.command()
async def modcoms(ctx):
    """Displays available moderator commands."""
    await send_mention(ctx, "Mod_commands: {} (See `fp!help` for more)".format(
        ", ".join(gvars.mod_coms)
    ))


@bot.command()
async def nobully(ctx):
    """
    Don't bully!
    
    Returns gif of Anti-Bully Ranger Akari Akaza
    (I'll kill you so hard you will die to death)
    """
    embed = discord.Embed(description="**Don't Bully!**")
    embed.set_image(url="https://zaxutic.ddns.net/FkPyramids/NoBully.gif")
    await ctx.send(embed=embed)


@bot.command()
async def invite(ctx):
    """
    Invite bot to server
    
    Gets link to invite bot to your own server
    """
    _id = bot.user.id
    url = f"https://discordapp.com/oauth2/authorize?client_id={_id}&scope=bot"

    embed = discord.Embed(
        colour=discord.Colour(0x33baf9),
        description=f"Invite me to your server [**here**]({url})"
    )

    embed.set_author(name=f"{ctx.author.name}",
                     icon_url=ctx.author.avatar_url_as(static_format="png"))

    await ctx.send(embed=embed)


@bot.command(aliases=["color"])
@from_guild()
async def colour(ctx, colour_hex: str):
    """
    Set colour role.

    Requires "Manage Roles" permission

    Removes any existing colour roles and deletes them if no longer used.
    Adds role with new colour if already existing in the server.
    If not, creates new role with colour and adds it to user.
    """

    # Add # to hex if not already included
    if colour_hex[0] != "#":
        colour_hex = "#" + colour_hex

    try:
        hex_value = int(colour_hex[1:] ,16)
    except ValueError:
        await send_mention(ctx, f"Usage: `{ctx.invoked_with} [hex code]`")
        return

    await send_mention(ctx, "Setting color to " + colour_hex)

    roles = ctx.message.guild.roles
    author = ctx.message.author

    # Remove any existing colour roles
    for role in filter(lambda r: r.name[0] == ("#"), roles):
        await author.remove_roles(role)

        if not role.members:
            await role.delete()

    # Check if role already exists
    role = discord.utils.get(roles, name=colour_hex)
    if role:
        await author.add_roles(role)
    else:
        colour_role = await ctx.message.guild.create_role(
            name=colour_hex,
            colour=discord.Colour(value=hex_value),
        )
        await colour_role.edit(position=len(roles) - 8)
        await author.add_roles(colour_role)

    await send_mention(ctx, f"Set {ctx.invoked_with} to {colour_hex}")


if __name__ == "__main__":
    gvars.init()
    local_vars = {"cooldown": 0}

    logger = logging.getLogger("discord")
    handler = logging.FileHandler(
        filename="log/discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)

    startup_extensions = ["cogs.modcoms", "cogs.owner_coms"]

    Channels = {}

    gvars.commands = load_file("commands.json")
    gvars.incoms = load_file("incoms.json")
    gvars.mod_coms = load_file("modcoms.json")
    gvars.mods = load_file("users.json")

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}.", file=sys.stderr)
            traceback.print_exc()

    bot.run(token)
