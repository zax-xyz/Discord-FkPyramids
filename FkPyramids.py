import discord
from discord.ext import commands as discord_commands
import asyncio
import datetime
import time
import logging
from termcolor import colored
import re

logger = logging.getLogger('discord')
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = discord_commands.Bot(
    command_prefix="fp!",
    status=discord.Activity(name="pyramids getting fk'd", type=3)
)

commandsList = {}
incomsList = {}
modComs = {}

modComsStd = ['fp!pyramid', 'fp!addcom', 'fp!delcom', 'fp!addincom',
              'fp!delincom', 'fp!addmodcom', 'fp!delmodcom', 'fp!react',
              'fp!s', 'fp!game', 'fp!react', 'fp!whitelist']
cooldown = 0
Channels = {}


def currentTime():
    t = datetime.datetime.now()
    return colored(t.strftime("%Y-%m-%d %H:%M:%S"), 'green')


def get_coms(f, dic):
    for line in f:
        com, out = line.split(maxsplit=1)
        try:
            dic[com] = " ".join(out)
        except IndexError:
            pass


# Delete channel entry from dictionary
def delete(chan):
    if chan in Channels:
        del Channels[chan]


async def send_mention(ctx, message):
    await ctx.send(ctx.author.mention + ' ' + message)


def from_guild():
    def predicate(ctx):
        return ctx.message.guild.id == 311016926925029376
    return discord_commands.check(predicate)


def is_mod():
    def predicate(ctx):
        return ctx.message.author.id in mods + admin_list
    return discord_commands.check(predicate)


def is_admin():
    def predicate(ctx):
        return ctx.message.author.id in admin_list
    return discord_commands.check(predicate)


with open("commands.txt", "r", encoding="utf-8") as commandsFile:
    get_coms(commandsFile, commandsList)

with open("incoms.txt", "r", encoding='utf-8') as incomsFile:
    get_coms(incomsFile, incomsList)

with open("modcoms.txt", "r", encoding='utf-8') as modcomsFile:
    get_coms(modcomsFile, modComs)

# Import moderator list
with open("users.txt", "r", encoding='utf-8') as userFile:
    mods = [int(line[:-1]) for line in userFile]

with open("token.txt", 'r') as tokenFile:
    token = tokenFile.readline()[:-1]


@bot.event
async def on_ready():
    global noBlockUsers
    global Owner
    global admin_list

    print(currentTime(), colored('Bot Online', 'grey', attrs=['bold']))
    print(colored('Name:', attrs=['bold']), bot.user.name)
    print(colored('ID:', attrs=['bold']), bot.user.id)
    noBlockUsers = [bot.user.id]
    bot_info = await bot.application_info()
    Owner = bot_info.owner.id
    admin_list = [Owner]


@bot.event
async def on_message(message):
    global cooldown

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

    if msg:
        for tup in mention_replace:
            for i in tup[0]:
                msg = re.sub(
                    i.mention,
                    lambda x: colored(tup[1](i), 'cyan', attrs=['bold']),
                    msg,
                    count=1
                )

        msg = re.sub(
            r'<:\w+:\d+>',
            lambda x: colored(f':{x.group().split(":")[1]}:', 'cyan'),
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
    if chanId in Channels and userId not in noBlockUsers:
        x = 1
        if len(msgParts) == 1:
            if (len(msgParts) == Channels[chanId]['len'] - 1 and
                    msg == Channels[chanId]['py']):
                # Completed 2-tier (baby) pyramid
                await channel.send(
                    "Baby pyramids don't count, you fucking degenerate.")
            Channels[chanId]['py'] = msg
            Channels[chanId]['len'] = 1
        elif len(msgParts) == 1 + Channels[chanId]['len']:
            Channels[chanId]['len'] += 1
            for part in msgParts:
                if part != Channels[chanId]['py']:
                    # Pyramid broken
                    delete(chanId)
                    x = 0
                    break
            if x and Channels[chanId]['len'] == 3:
                # Pyramid peaks
                for i in [1, 2, 3, 2, 1]:
                    await channel.send("no " * i)
                delete(chanId)
        else:
            # Pramid broken
            delete(chanId)
    elif len(msgParts) == 1:
        # Pyramid start
        Channels[chanId] = {'len': 1, 'py': msg}

    if userId != bot.user.id and msgParts:
        com = msgParts[0]
        # Custom commands
        if userId in mods + admin_list and com in modComs:
            await channel.send(modComs[com])
        elif com in commandsList:
            await channel.send(commandsList[com])

        # In_commands
        if time.time() - cooldown > 30:
            try:
                key = next(k for k in incomsList if k in msg.lower())
            except StopIteration:
                key = None
            if key:
                await channel.send(incomsList[key])

    await bot.process_commands(message)


@bot.command(brief="Sends message to channel by ID.")
@discord_commands.is_owner()
async def send(ctx, channelId: int, *, message: str):
    await bot.get_channel(channelId).send(message)


@bot.command()
async def commands(ctx):
    await send_mention(ctx, "Commands: " + ', '.join(commandsList.keys()))


@bot.command()
async def admins(ctx):
    await send_mention(ctx, "Admins: " + ', '.join(mods))


@bot.command()
async def incoms(ctx):
    await send_mention(ctx, "In_commands: " + ', '.join(incomsList.keys()))


@bot.command()
async def modcoms(ctx):
    await send_mention(ctx, "Mod_commands: " + ', '.join(modComs + modComsStd))


@bot.command()
async def nobully(ctx):
    nobullyEmbed = discord.Embed(description="**Don't Bully!**")
    nobullyEmbed.set_image(url="https://i.imgur.com/jv7O5aj.gif")
    await ctx.send(embed=nobullyEmbed)


@bot.command()
@from_guild()
async def colour(ctx, cHex: str, aliases=['color']):
    # Requires "Manage Roles" permission

    # Add # to hex if not already included
    cHex = cHex if cHex[0] == ('#') else '#' + cHex
    hexLetters = ['a', 'b', 'c', 'd', 'e', 'f']

    if all((char.isdigit() or char in hexLetters) for char in cHex[1:]):
        await send_mention(ctx, "Setting color to " + cHex)
        roles = ctx.message.guild.roles
        author = ctx.message.author

        # Remove any existing colour roles
        for r in filter(lambda r: r.name[0] == ('#'), guild_roles):
            await author.remove_roles(r)

        # Check if role already exists
        role = discord.utils.get(roles, name=cHex)
        if role:
            await author.add_roles(role)
        else:
            colourRole = await ctx.message.guild.create_role(
                name="#" + cHex,
                colour=discord.Colour(value=int(cHex[1:], 16)),
                position=len(roles) - 8
            )
            await author.add_roles(colourRole)
        await send_mention(ctx, f"Set {ctx.invoked_with} to {cHex}")
    else:
        await send_mention(ctx, f"Usage: `{ctx.invoked_with} [hex code]`")


@bot.command(brief="Creates pyramids.")
@is_mod()
async def pyramid(ctx, length: int, *, message: str):
    length += 1
    for i in [length - abs(i) for i in range(-length + 1, length)]:
        await ctx.send(message * i)


@bot.command(brief="Deletes messages.")
@is_mod()
async def delmsg(ctx, n: int):
    # Requires "Manage Messages" permission
    async for m in ctx.message.channel.history(limit=n):
        try:
            await m.delete()
        except discord.errors.Forbidden:
            print("Insufficient permissions")


@bot.command(brief="Adds a command.")
@is_mod()
async def addcom(ctx, command: str, *, output: str):
    commandsList[command] = output
    with open("commands.txt", "a") as commandsFile:
        commandsFile.write(f"{command} {output}\n")
    await send_mention(ctx, f'Added command "{command}"')


@bot.command(brief="Deletes command.")
@is_mod()
async def delcom(ctx, command: str):
    if command in commandsList:
        del commandsList[command]
        with open('commands.txt') as f:
            lines = f.readlines()
        with open("commands.txt", 'w') as commandsFile:
            for line in filter(lambda l: l.split()[0] != command, lines):
                commandsFile.write(line + '\n')
        await send_mention(ctx, f'Removed command "{command}"')
    else:
        await send_mention(ctx, f'Command "{command}" doesn\'t exist')


@bot.command(brief="Adds in_command.")
@is_mod()
async def addincom(ctx, in_com: str, *, output: str):
    incomsList[in_com] = output
    with open("incoms.txt", "a") as incomsFile:
        incomsFile.write(f"{in_com} {output}\n")
    await send_mention(ctx, f'Added in_command "{in_com}"')


@bot.command(brief="Deletes in_command.")
@is_mod()
async def delincom(ctx, in_com: str):
    if in_com in incomsList:
        del incomsList[in_command]
        with open('incoms.txt') as f:
            lines = f.readlines()
        with open("incoms.txt", "w") as incomsFile:
            for line in filter(lambda l: l.split()[0] != in_com, lines):
                incomsFile.write(line + '\n')
        await send_mention(ctx, f'Removed in_command "{in_com}"')
    else:
        await send_mention(ctx, f'In_command "{in_com}" doesn\'t exist')


@bot.command(brief="Add mod commmand")
@is_mod()
async def addmodcom(ctx, modcom: str, *, output: str):
    modComs[modcom] = output
    with open("modcom.txt", "a") as modcomsFile:
        modcomsFile.write(f"{command} {output}\n")
    await channel.send(f'{mention} Added mod command "{modcom}"')


@bot.command(brief="Delete mod command")
@is_mod()
async def delmodcom(ctx, modcom: str):
    del modComs[modcom]
    with open('modComsStd.txt') as f:
        lines = f.readlines()
    with open("modComsStd.txt", "w") as modcomsFile:
        for line in filter(lambda l: l.split()[0] != modcom, lines):
            modcomsFile.write(line + '\n')
    await send_mention(ctx, f'Deleted mod command "{modcom}"')


@bot.command(brief="Delete all unused roles in server")
@is_mod()
async def delroles(ctx):
    # Requires "Manage Roles" permission.
    # Doesn't usually delete all roles at once,
    # requires multiple executions.

    roles = ctx.messaage.guild.roles
    member_roles = set([u.roles for u in ctx.message.guild.members])
    used_roles = filter(lambda r: r in member_roles, roles)
    for r in filter(lambda r: r not in used_roles, roles):
        await r.delete()
        await ctx.send('Deleted role "{r.name}".')
    await ctx.send("Deleted unused roles.")


@bot.command(brief="Add reaction to last [n] messages in channel")
@is_mod()
async def react(ctx, n: int, em: str):
    if em.isdigit():
        # Get emoji by ID
        em = discord.utils.get(bot.emojis(), id=int(em))
        if em:
            async for i in channel.history(limit=num):
                await i.add_reaction(em)
        else:
            await send_mention(ctx, 'Could not find emote')
    else:
        # Get emoji directly using string
        try:
            async for i in channel.history(limit=num):
                await i.add_reaction(em[2:-1])
        except (discord.errors.NotFound, discord.errors.InvalidArgument):
            await send_mention(ctx, 'Usage: `!fpreact [n] [emote]`')
        except discord.errors.Forbidden:
            await send_mention(ctx, 'Could not react to message.')


@bot.command(brief="Whitelist user from pyramid blocking")
@is_mod()
async def whitelist(ctx, user: int):
    noBlockUsers.append(user)


@bot.command(brief="Remove user from pyramid blocking whitelist")
@is_mod()
async def blacklist(ctx, user: int):
    if user in noBlockUsers:
        noBlockUsers.remove(user)
    else:
        await send_mention(ctx, f'{user} is not whitelisted')


@bot.command(brief="Send message [n] amount of times in a row")
@is_mod()
async def s(ctx, n: int, message: str):
    for i in range(n):
        await ctx.send(messaage)


@bot.command(brief="Change activity status of bot")
@is_mod()
async def status(ctx, aType: str, *, name: str):
    if aType == 'playing':
        aType = 1
    elif aType == 'listening':
        aType = 2
    elif aType == 'watching':
        aType = 3
    await bot.change_presence(
        activity=discord.Activity(name=name, type=aType))
    await send_mention(ctx, f'Set activity to "{name}"')


@bot.command(brief="Add user to moderator list")
@is_admin()
async def adduser(ctx, user: str):
    if ctx.message.mentions:
        user = ctx.message.mentions[0].id
    with open("users.txt", "a", encoding='utf-8') as userFile:
        userFile.write(user + '\n')
        mods.append(int(user))
    await send_mention(ctx, f'Added {user} to moderators')


@bot.command(brief="Remove user from moderator list")
@is_admin()
async def deluser(ctx, user: str):
    # Remove user from moderator list
    if ctx.message.mentions:
        user = ctx.message.mentions[0].id
    mods.remove(int(user))
    with open('users.txt') as f:
        lines = f.readlines()
    with open("users.txt", "w", encoding='utf-8') as userFile:
        for line in lines:
            if line[:-1] != user:
                userFile.write(line)
    await send_mention(ctx, f'Removed {user} from moderators.')


@bot.command(brief="Shutdown bot")
@is_admin()
async def shutdown(ctx):
    await ctx.send('Shutting down client.')
    await bot.close()


@bot.command(brief="Clear internal bot cache")
@is_admin()
async def clear(ctx):
    bot.clear()
    await ctx.send('Internal cache cleared.')


bot.run(token)
