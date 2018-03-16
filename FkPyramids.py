import discord
from discord.ext import commands
import asyncio
import os
import datetime
import time
import logging

Owner = 135678905028706304  # Put your user ID here

# discord.py logging (WARNING level)
logger = logging.getLogger('discord')
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Initiate bot instance
Client = discord.Client()
bot = commands.Bot(command_prefix="!")

# Initiate dictionary variables for commands
commandsList = {}
incomsList = {}
modcomsList = {}

modcoms = ["!pyramid", '!fpaddcom', '!fpdelcom', '!fpaddincom','!fpdelincom',
           '!fpaddmodcom', '!fpdelmodcom', '!fpreact', '!s', '!fpgame',
           '!fpreact', '!fpwhitelist']
admins = [Owner]
cooldown = 0
Channels = {}

# Import commands from files
with open("commands.txt", "r", encoding="utf-8") as commandsFile:
    for line in commandsFile:
        lineParts = line.split()
        try:
            commandsList[lineParts[0].lower()] = " ".join(lineParts[1:])
        except IndexError:
            pass
with open("incoms.txt", "r", encoding='utf-8') as incomsFile:
    for line in incomsFile:
        lineParts = line.split()
        try:
            incomsList[lineParts[0].lower()] = ' '.join(lineParts[1:])
        except:
            pass
with open("modcoms.txt", "r", encoding='utf-8') as modcomsFile:
    for line in modcomsFile:
        lineParts = line.split()
        try:
            modcomsList[lineParts[0].lower()] = ' '.join(lineParts[1:])
        except:
            pass

# Import moderator list
with open("users.txt", "r", encoding='utf-8') as userFile:
    userList = [int(line[:-1]) for line in userFile]

# Import bot token
with open("token.txt", 'r') as tokenFile:
    token = tokenFile.readline()[:-1]

# Get current time in (H)H:MM:SS format
def currentTime():
    t = datetime.datetime.now()
    return "{:%H:%M:%S} ".format(t)

# Delete channel entry from dictionary
def delete(chan):
    try:
        del Channels[chan]
    except KeyError:
        pass

# Bot starts
@bot.event
async def on_ready():
    global noBlockUsers
    print(f"{currentTime()} Bot Online")
    print(f"Name: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    noBlockUsers = [bot.user.id]
    await bot.change_presence(game=discord.Game(
        name="pyramids getting fk'd", type=3))

# Handler for each message received
@bot.event
async def on_message(message):
    global voice
    global vChannel
    global cooldown

    # Initiate & assign variables from message
    username = str(message.author)
    mention = message.author.mention
    userId = message.author.id
    msg = str(message.content)
    msgParts = msg.split()
    channel = message.channel
    chanId = channel.id
    guild = message.guild
    guildId = guild.id

    # Print message with time and username
    print(f'{currentTime()} {username}: {msg}')

    # Assign varables for commands
    com = None
    com2 = None
    com3 = None
    try:
        com = msgParts[0].lower()
        com2 = msgParts[1].lower()
        com3 = msgParts[2]
    except:
        pass

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
            if x:
                if Channels[chanId]['len'] == 3:
                    # Pyramid peaks, block
                    await channel.send("no")
                    delete(chanId)
        else:
            # Pramid broken
            delete(chanId)
    elif len(msgParts) == 1:
        # Pyramid start
        Channels[chanId] = {'len': 1, 'py': msg}

    # Direct messages
    if isinstance(channel, discord.abc.PrivateChannel):
        if userId == Owner and com == '!send':
            # Send message to specified channel using ID
            if len(msgParts) >= 3:
                await bot.get_channel(int(com2)).send(' '.join(msgParts[2:]))
            else:
                await channel.send("Usage: `!send {channel id} {message}`")

    # If user is not the bot
    if userId != bot.user.id:
        # Handle commands
        if com in commandsList:
            await channel.send(commandsList[com])
        elif time.time() - cooldown > 30:
            # In_commands - if key is anywhere in message, not just beginning
            for key in incomsList:
                if key in msg.lower():
                    await channel.send(incomsList[key])
                    break
            cooldown = time.time()
        if com in ['color', 'colour'] and guildId == 311016926925029376:
            # Requires "Manage Roles" permission
            if com2:
                cHex = com2.strip('#')
                # Letters used in hexadecimals
                # Used to find if hex code given is valid
                hexLetters = ['a', 'b', 'c', 'd', 'e', 'f']
                isHex = True

                for char in cHex:
                    # Check if hex code is valid
                    if not char.isdigit() and char not in hexLetters:
                        isHex = False
                        break

                if isHex:
                    await channel.send(f"{mention} Setting color to #{cHex}")
                    for r in message.author.roles:
                        # Check if user already has a color role
                        # If so, remove it
                        if r.name.startswith('#'):
                            await message.author.remove_roles(r)
                    roleFound = False
                    for r in guild.roles:
                        # Check if role for color already exists
                        # If so, give user this roles instead of
                        # Creating a new one
                        if r.name == '#' + cHex:
                            roleFound = True
                            await message.author.add_roles(r)
                            break
                    if roleFound:
                        # Creat and assign role to user if
                        # no existing role found
                        colorRole = await guild.create_role(name="#" + cHex,
                            colour=discord.Colour(value=int(cHex, 16)))
                        await colorRole.edit(position=len(guild.roles) - 8)
                        await message.author.add_roles(colorRole)
                    await channel.send(f"{mention} Set colour to #{cHex}")
                else:
                    await channel.send(f"{mention} Usage: `{com} [hex code]`")
            else:
                await channel.send(f"{mention} Usage: `{com} [hex code]`")
        # Basic commands
        elif com == '!fpcommands':
            await channel.send(
            f"{mention} Commands: {', '.join(commandsList.keys())}")
        elif com == '!fpadmins':
            await channel.send(f"{mention} Admins: {', '.join(userList)}")
        elif com == '!fpincoms':
            await channel.send(
                f"{mention} In_commands: {', '.join(incomsList.keys())}")
        elif com == '!fpmodcoms':
            await channel.send(
                f"{mention} Mod commands: {', '.join(modcomsList + modcoms)}")
        elif com == '!nobully':
            # NoBully
            nobullyEmbed = discord.Embed(description="**Don't Bully!**")
            nobullyEmbed.set_image(url="https://i.imgur.com/jv7O5aj.gif")
            await channel.send(embed=nobullyEmbed)

    if userId in userList + admins:
        # If user is a moderator or admin
        if com == "!pyramid" and len(msgParts) >= 3:
            # Send message an ascending and descending amount of time,
            # Creating a 'pyramid'
            p = ' '.join(msgParts[2:]) + ' '
            pLen = int(com2) + 1
            for i in range(1, pLen):
                await channel.send(p * i)
            for i in range(2, pLen):
                await channel.send(p * (pLen - i))
        elif com == "!fpdelmsg":
            # Delete last {n} messages in channel
            # Requires "Manage Messages" permission
            if com2.isdigit():
                com2 = int(com2)
                async for m in channel.history(limit=com2):
                    try:
                        await m.delete()
                    except discord.errors.Forbidden:
                        print("Insufficient permissions")
                        pass
        elif com == "!fpaddcom":
            # Add basic command
            if len(msgParts) >= 3:
                with open("commands.txt", "a") as commandsFile:
                    commandsList[com2] = " ".join(msgParts[2:])
                    commandsFile.write(' '.join(msgParts[1:]) + '\n')
                await channel.send(f'{mention} Added command "{com2}"')
            else:
                await channel.send(
                    f"{mention} Usage: `!fpaddcom [command] [output]`")
        elif com == '!fpdelcom':
            # Delete basic command
            if len(msgParts) == 2:
                if com2 in commandsList:
                    del commandsList[com2]
                    with open('commands.txt') as f:
                        # Temporarily store data from file
                        lines = f.readlines()
                    with open("commands.txt", 'w') as commandsFile:
                        # Wipe file and rewrite data to it,
                        # Excluding certain unwanted lines
                        for line in lines:
                            try:
                                if not line.split()[0] == com2:
                                    commandsFile.write(line + '\n')
                            except:
                                pass
                    await channel.send(f'{mention} Removed command "{com2}"')
                else:
                    await channel.send(
                        f'{mention} Command "{com2}" doesn\'t exist')
            else:
                await channel.send("Usage: `!fpdelcom [command]`")
        elif com == "!fpaddincom":
            # Add in_command
            with open("incoms.txt", "a") as incomsFile:
                incomsFile.write(' '.join(msgParts[1:]) + '\n')
                incomsList[com2] = ' '.join(msgParts[2:])
            await channel.send(f'{mention} Added in_command "{com2}"')
        elif com == '!fpdelincom':
            # Delete in_command
            if com2 in incomsList:
                del incomsList[com2]
                with open('incoms.txt') as f:
                    # Temporarily store data from file
                    lines = f.readlines()
                with open("incoms.txt", "w") as incomsFile:
                    # Wipe file and rewrite data to it,
                    # Excluding certain unwanted lines
                    for line in lines:
                        if not line.split()[0] == com2:
                            incomsFile.write(line + '\n')
                await channel.send(f'{mention} Removed in_command "{com2}"')
            else:
                await channel.send(
                    f'{mention} In_command "{com2}" doesn\'t exist')
        elif com == '!fpaddmodcom':
            # Add basic moderator command
            with open("modcoms.txt", "a") as modcomsFile:
                modcomsList[com2] = " ".join(msgParts[2:])
                modcomsFile.write(' '.join(msgParts[1:] + '\n'))
            await channel.send(f'{mention} Added mod command "{com2}"')
        elif com == '!fpdelmodcom':
            # Delete basic moderator command
            if len(msgParts) == 2:
                del modcomsList[com2]
                with open('modcoms.txt') as f:
                    # Temporarily store data from file
                    lines = f.readlines()
                with open("modcoms.txt", "w") as modcomsFile:
                    # Wipe file and rewrite data to it,
                    # Excluding certain unwanted lines
                    for line in lines:
                        if line:
                            if not line.split()[0].lower() == com2:
                                modcomsFile.write(line + '\n')
                await channel.send(f'{mention} Deleted mod command "{com2}"')
        elif com == '!fpdelroles':
            # Requires "Manage Roles" permission.
            # Doesn't usually delete all roles at once,
            # requires multiple executions.

            # Commented code for debugging
            roles = guild.roles
            members = guild.members
            # print("Roles:", (len(roles))
            # print("Roles:", ', '.join([r.name for r in roles]))
            usedRoles = []
            for r in roles:
                for u in members:
                    if r in u.roles:
                        usedRoles.append(r)
                        break
            # print("Used:", ', '.join([r.name for r in usedRoles]))
            for r in usedRoles:
                roles.remove(r)
            # print("Unused:", ', '.join([r.name for r in roles]))
            for r in roles:
                await r.delete()
                await channel.send('Deleted role "{r.name}".')
            await channel.send("Deleted unused roles.")
        elif com == '!fpreact':
            # React to last {n} messages in channel with specificed emoji
            num = int(com2)
            if com3.isdigit():
                # Get reaction emoji by ID
                for em in bot.emojis():
                    if em.id == com3:
                        e = em
                        async for i in channel.history(limit=num):
                            await i.add_reaction(e)
                        break
            else:
                # Get reaction emoji directly using string
                e = com3
                try:
                    async for i in channel.history(limit=num):
                        await i.add_reaction(e[2:-1])
                except:
                    await channel.send(
                        '{mention} Usage: `!fpreact [n] [emote]`')
        elif com == '!fpwhitelist':
            # Whitelist user from pyramid blocking
            if com2.isdigit():
                noBlockUsers.append(com2)
            else:
                await channel.send(
                    f'{mention} Usage: `!fpwhitelist [user id]`')
        elif com == '!fpblacklist':
            # Remove user from pyramid blocking whitelist
            if com2.isdigit():
                if com2 in noBlockUsers:
                    noBlockUsers.remove(com2)
                else:
                    await channel.send(f'{mention} {com2} is not whitelisted')
            else:
                await channel.send(
                    f'{mention} Usage: `!fpblacklist [user id]`')

        if com in modcomsList:
            await channel.send(modcomsList[com])
        elif com == "!s" and len(msgParts) >= 3:
            # Send message [n] amount of times in a row
            n = int(com2)
            for i in range(n):
                await channel.send(' '.join(msgParts[2:]))
        elif com == "!fpstatus":
            # Change playing/streaming/listening/watching status
            await bot.change_presence(game=discord.Game(
                name=' '.join(msgParts[2:]), type=int(com2)))
            await channel.send(
                f'{mention} Set game to "{" ".join(msgParts[2:])}"')
        """
        elif com == '!fpvoice':  # Incomplete
            if len(msgParts) >= 2:
                if com2 == 'join':
                    # Join voice channel
                    if len(msgParts) == 3:
                        # Get voice channel by ID
                        vChannel = bot.get_channel(int(com3))
                    elif len(msgParts) == 2:
                        # Get voice channel user is currently in
                        vChannel = message.author.voice.channel
                    voice = await vChannel.connect()
                    await channel.send(f'Joined "{vChannel.name}"')
                elif com2 == 'leave':
                    # Leave voice channel
                    for c in bot.voice_clients:
                        if c.guild == guild:
                            await voice.disconnect()
                            await channel.send('Left "{vChannel.name}"')
            else:
                await channel.send('Missing argument: `join`, `leave`')
        """

    if userId in admins:
        if com == "!fpadduser" and len(msgParts) == 2:
            # Add user to moderator list
            if message.mentions:
                user = message.mentions[0].id
            else:
                user = int(com2)
            with open("users.txt", "a", encoding='utf-8') as userFile:
                userFile.write(str(user) + '\n')
                userList.append(user)
            await channel.send(f'{mention} Added {user} to moderators')
        elif com == "!fpdeluser":
            # Remove user from moderator list
            if message.mentions:
                user = message.mentions[0].id
            else:
                user = str(com2)
            userList.remove(user)
            with open('users.txt') as f:
                # Temporarily store data from file
                lines = f.readlines()
            with open("users.txt", "w", encoding='utf-8') as userFile:
                # Wipe file and rewrite data to it,
                # Excluding certain unwanted lines
                for line in lines:
                    if line[:-1] != str(user):
                        userFile.write(line)
            await channel.send(f'{mention} Removed {user} from moderators.')
        elif com == "!fpshutdown":
            # Shut down bot completely
            await channel.send('Shutting down client.')
            await bot.close()
        elif com == "!fpclear":
            # Clear the bot's internal cache
            bot.clear()
            await channel.send('Internal cache cleared.')

bot.run(token)
