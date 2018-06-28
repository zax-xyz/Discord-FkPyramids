import discord
from discord.ext import commands

import asyncio
import logging
import datetime
import time
import itertools
import sys
import json
import re
import traceback
from termcolor import colored

import global_settings as gvars
from config.auth import token
from config import config


gvars.init()
local_vars = {'cooldown': 0}

logger = logging.getLogger('discord')
handler = logging.FileHandler(
    filename='log/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(
    command_prefix=config.prefix,
    activity=discord.Activity(
        name=config.activity_name,
        type=config.activity_type
    )
)

startup_extensions = ['cogs.modcoms', 'cogs.owner_coms']

Channels = {}


def currentTime():
    t = datetime.datetime.now()
    return colored(t.strftime("%Y-%m-%d %H:%M:%S"), 'green')


# Delete channel entry from dictionary
def delete(chan):
    if chan in Channels:
        del Channels[chan]


def load_file(filename):
    with open("config/" + filename, "r", encoding="utf-8") as f:
        return json.load(f)

gvars.commands = load_file("commands.json")
gvars.incoms = load_file("incoms.json")
gvars.modComs = load_file("modcoms.json")
gvars.mods = load_file("users.json")


async def send_mention(ctx, message):
    await ctx.send(ctx.author.mention + ' ' + message)


def from_guild():
    def predicate(ctx):
        return ctx.message.guild.id == 311016926925029376
    return commands.check(predicate)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(f"Command `{ctx.invoked_with}` not found.")

    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__,
                              file=sys.stderr)

@bot.event
async def on_ready():
    print(currentTime(), colored('Bot Online', 'green', attrs=['bold']))
    print(colored('Name:', 'green', attrs=['bold']), bot.user.name)
    print(colored('ID:', 'green', attrs=['bold']), bot.user.id)

    gvars.noBlockUsers = [bot.user.id, 135678905028706304]

    bot_info = await bot.application_info()
    local_vars['Owner'] = bot_info.owner.id


@bot.event
async def on_message(message):
    userId = message.author.id
    msg = str(message.content)
    msgParts = msg.split()
    channel = message.channel
    chanId = channel.id
    name, disc = str(message.author).rsplit('#', 1)
    disc = '#' + disc

    mention_replace = (
        (message.mentions, lambda x: '@' + x.name),
        (message.channel_mentions, lambda x: '#' + x.name),
        (message.role_mentions, lambda x: 'r@' + x.name)
    )

    sub_tup = (
        (r'<a?:\w+:\d+>', lambda x: f':{x.split(":")[1]}:'),
    )

    if msg:
        for tup in mention_replace:
            for i in tup[0]:
                msg = re.sub(
                    i.mention,
                    lambda x: colored(tup[1](i), 'cyan', attrs=['bold']),
                    msg,
                )

        for tup in sub_tup:
            msg = re.sub(
                tup[0],
                lambda x: colored(tup[1](x.group()), 'cyan'),
                msg
            )

    else:
        msg = colored(
            'Unable to display message (image, embed, etc)',
            'red',
            attrs=['bold']
        )

    if message.attachments:
        for attach in message.attachments:
            msg += ' ' + colored(attach.url, 'cyan')

    print('{} {}  {}{}: {}'.format(
        currentTime(),
        colored(f'[{message.guild.name}]', attrs=['bold']),
        colored(
            name,
            'blue' if message.author != bot.user else 'cyan',
            attrs=['bold']),
        colored(disc, 'grey', attrs=['bold']),
        msg
    ))

    # Pyramid blocking
    if userId not in gvars.noBlockUsers:
        if chanId in Channels:
            if len(msgParts) == 1:
                if (len(msgParts) == Channels[chanId]['len'] - 1 and
                        msg == Channels[chanId]['py']):
                    # Completed 2-tier (baby) pyramid
                    await send_mention(channel,
                        "Baby pyramids don't count, you fucking degenerate.")

                Channels[chanId]['py'] = msg
                Channels[chanId]['len'] = 1
            elif len(msgParts) == 1 + Channels[chanId]['len']:
                Channels[chanId]['len'] += 1

                for part in msgParts:
                    if part != Channels[chanId]['py']:
                        # Pyramid broken
                        del Channels[chanId]
                        break
                else:
                    if Channels[chanId]['len'] == 3:
                        # Pyramid peaks
                        for i in [1, 2, 3, 2, 1]:
                            await channel.send("no " * i)

                        del Channels[chanId]
            else:
                # Pramid broken
                del Channels[chanId]
        elif len(msgParts) == 1:
        # Pyramid start
            Channels[chanId] = {'len': 1, 'py': msg}
    elif chanId in Channels:
        del Channels[chanId]

    if userId != bot.user.id and msgParts:
        com = msgParts[0]
        # Custom commands
        if userId in gvars.mods + [local_vars['Owner']] and com in gvars.modComs:
            return await channel.send(gvars.modComs[com])
        elif com in gvars.commands:
            return await channel.send(gvars.commands[com])

        # In_commands
        if time.time() - local_vars['cooldown'] > 30:
            try:
                key = next(k for k in gvars.incoms if k in msg.lower())
            except StopIteration:
                key = None

            if key:
                await channel.send(gvars.incoms[key])
                local_vars['cooldown'] = time.time()

    await bot.process_commands(message)


@bot.command(brief="Displays available user-added commands.", name="commands")
async def _commands(ctx):
    await send_mention(ctx, "Commands: {} (See `fp!help` for more)".format(
        ', '.join(gvars.commands)
    ))


@bot.command(brief="Displays moderators for FkPyramids.")
async def mods(ctx):
    mods = [*gvars.mods]
    mods_men = [bot.get_user(x).mention if bot.get_user(x) else x for x in mods]
    await send_mention(ctx, "Mods: " + ', '.join([str(x) for x in mods_men]))


@bot.command(brief="Displays available in_commands.")
async def incoms(ctx):
    await send_mention(ctx, "In_commands: " + ', '.join(gvars.incoms))


@bot.command(brief="Displays available moderator commands.")
async def modcoms(ctx):
    await send_mention(ctx, "Mod_commands: {} (See `fp!help` for more)".format(
        ', '.join(gvars.modComs)
    ))


@bot.command(brief="Don't bully!")
async def nobully(ctx):
    embed = discord.Embed(description="**Don't Bully!**")
    embed.set_image(url="https://zaxutic.ddns.net/FkPyramids/NoBully.gif")
    await ctx.send(embed=embed)


@bot.command(brief="Set colour role.", aliases=['color'])
@from_guild()
async def colour(ctx, cHex: str):
    # Requires "Manage Roles" permission

    # Add # to hex if not already included
    cHex = cHex if cHex[0] == ('#') else '#' + cHex
    hexLetters = ['a', 'b', 'c', 'd', 'e', 'f']

    if all((char.isdigit() or char in hexLetters) for char in cHex[1:]):
        await send_mention(ctx, "Setting color to " + cHex)

        roles = ctx.message.guild.roles
        author = ctx.message.author

        # Remove any existing colour roles
        for r in filter(lambda r: r.name[0] == ('#'), roles):
            await author.remove_roles(r)

            if not r.members:
                await r.delete()

        # Check if role already exists
        role = discord.utils.get(roles, name=cHex)
        if role:
            await author.add_roles(role)
        else:
            colourRole = await ctx.message.guild.create_role(
                name=cHex,
                colour=discord.Colour(value=int(cHex[1:], 16)),
            )
            await colourRole.edit(position=len(roles) - 8)

            await author.add_roles(colourRole)
        await send_mention(ctx, f"Set {ctx.invoked_with} to {cHex}")
    else:
        await send_mention(ctx, f"Usage: `{ctx.invoked_with} [hex code]`")


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

    bot.run(token)
