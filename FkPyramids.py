import discord
from discord.ext import commands
import asyncio
import os
import datetime
import time
import logging

Owner = '135678905028706304'  # Put your user ID here

logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so.0.6.1')

Client = discord.Client()
bot = commands.Bot(command_prefix="!")
commandsList = {}
incomsList = {}
modcomsList = {}
regmodcoms = ["!pyramid", '!fpaddcom', '!fpdelcom', '!fpaddincom', '!fpdelincom', '!fpaddmodcom', '!fpdelmodcom', '!fpreact', '!s', '!fpgame', '!fpreact', '!fpwhitelist']
admins = [Owner]
cooldown = 0
Channels = {}

with open("commands.txt", "r", encoding="utf-8") as commandsFile, open("users.txt", "r", encoding='utf-8') as userFile, open("incoms.txt", "r", encoding='utf-8') as incomsFile, open("modcoms.txt", "r", encoding='utf-8') as modcomsFile, open("token.txt", 'r') as tokenFile:
    for line in commandsFile:
        lineParts = line.split()
        try:
            commandsList[lineParts[0].lower()] = " ".join(lineParts[1:])
        except:
            pass
    userList = [line[:-1] for line in userFile]
    for line in incomsFile:
        lineParts = line.split()
        try:
            incomsList[lineParts[0].lower()] = ' '.join(lineParts[1:])
        except:
            pass
    for line in modcomsFile:
        lineParts = line.split()
        try:
            modcomsList[lineParts[0].lower()] = ' '.join(lineParts[1:])
        except:
            pass
    token = tokenFile.readline()[:-1]

async def pyBlock(bbyPyBlock, lst):
    x = 1
    if len(msgParts) == 1:
        if len(msgParts) == Channels[chanId]['len'] - 1 and msg == Channels[chanId]['py']:
            await bot.send_message(chan, "Baby pyramids don't count, you fucking degenerate. {}".format(bbyPyBlock))
        Channels[chanId]['py'] = msg
        Channels[chanId]['len'] = 1
    elif len(msgParts) == 1 + Channels[chanId]['len']:
        Channels[chanId]['len'] += 1
        for part in msgParts:
            if part != Channels[chanId]['py']:
                del Channels[chanId]
                x = 0
                break
        if x:
            if Channels[chanId]['len'] == 3:
                for i in lst:
                    await bot.send_message(chan, "no")
                del Channels[chanId]
    else:
        del Channels[userId]

def currentTime():
    t = datetime.datetime.now()
    return "{:%H:%M:%S} ".format(t)

@bot.event
async def on_ready():
    global noBlockUsers
    print("{} Bot Online".format(currentTime()))
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    noBlockUsers = [bot.user.id]
    await bot.change_presence(game=discord.Game(name='NoBully'))

@bot.event
async def on_message(message):
    global voice
    global vChannel
    global auMention
    global userId
    global chan
    global cooldown
    username = str(message.author)
    auMention = message.author.mention
    userId = message.author.id
    msg = str(message.content)
    msgParts = msg.split()
    chan = message.channel
    chanId = chan.id
    print('{} {}: {}'.format(currentTime(), username, msg))
    com = None
    com2 = None
    com3 = None
    try:
        com = msgParts[0].lower()
        com2 = msgParts[1].lower()
        com3 = msgParts[2]
    except:
        pass
    if chan.is_private:  # DMs
        if chanId in Channels:
            pyBlock('', [1])
        elif len(msgParts) == 1:
            Channels[chanId] = {'len': 1, 'py': msg}

        if userId == Owner:
            if com == '!send':
                if len(msgParts) >= 3:
                    await bot.send_message(bot.get_channel(com2), ' '.join(msgParts[2:]))
    else:
        if chanId in Channels:
            if userId not in noBlockUsers and userId != message.server.owner.id:
                pyBlock(auMention, [1,2,3,2,1])
            else:
                del Channels[chanId]
        elif len(msgParts) == 1:
            Channels[chanId] = {'len': 1, 'py': msg}

    if userId != bot.user.id:
        if com in commandsList:
            await bot.send_message(chan, commandsList[com])
        elif time.time() - cooldown > 30:
            for key in incomsList:
                if key in msg.lower():
                    await bot.send_message(chan, incomsList[key])
                    break
            cooldown = time.time()
        if (com == "!color" or com == "!colour") and message.server.id == "311016926925029376":  # Requires "Manage Roles" permission
            if com2:
                colorHex = com2.strip('#')
                if colorHex.isdigit():
                    await bot.send_message(chan, "{} Setting color to #{}".format(auMention, colorHex))
                    for r in message.author.roles:
                        if r.name.startswith('#'):
                            await bot.remove_roles(message.author, r)
                    for r in message.server.roles:
                        if r.name == '#{}'.format(colorHex):
                            await bot.add_roles(message.author, r)
                            break
                    else:
                        colorRole = await bot.create_role(message.server, name="#{}".format(colorHex), colour=discord.Colour(value=int(colorHex, 16)))
                        await bot.move_role(message.server, colorRole, len(message.server.roles)-8)
                        await bot.add_roles(message.author, colorRole)
                    await bot.send_message(chan, "{} Set colour to #{}".format(auMention, colorHex))
            else:
                await bot.send_message(chan, "{} Syntax: `{} [{} hex code]`".format(auMention, com, com[1:]))
        elif com == '!fpcommands':
            await bot.send_message(chan, "{} Commands are: {}".format(auMention, ', '.join(commandsList.keys())))
        elif com == '!fpusers':
            await bot.send_message(chan, "{} Authorised users are: {}".format(auMention, ', '.join(userList)))
        elif com == '!fpincoms':
            await bot.send_message(chan, "{} In_commands are: {}".format(auMention, ', '.join(incomsList.keys())))
        elif com == '!fpmodcoms':
            await bot.send_message(chan, "{} Mod commands are: {}, {}".format(auMention, ', '.join(modcomsList), ', '.join(regmodcoms)))
        elif com == '!nobully':
            nobullyEmbed = discord.Embed(description="**Don't Bully!**")
            nobullyEmbed.set_image(url="https://i.imgur.com/jv7O5aj.gif")
            await bot.send_message(chan, embed=nobullyEmbed)

    if userId in userList + admins:
        if com == "!pyramid" and len(msgParts) >= 3:
            p = "{} ".format(' '.join(msgParts[2:]))
            pLen = int(com2) + 1
            for i in range(1, pLen):
                await bot.send_message(chan, p * i)
            for i in range(2, pLen):
                await bot.send_message(chan, p * (pLen - i))
        elif com == "!delmsg":  # Requires "Manage Messages" permission
            if com2.isdigit():
                com2 = int(com2)
                async for m in bot.logs_from(chan, com2):
                    await bot.delete_message(m)
        elif com == "!fpaddcom":
            if len(msgParts) >= 3:
                with open("commands.txt", "a", encoding="utf-8") as commandsFile:
                    commandsList[com2] = " ".join(msgParts[2:])
                    commandsFile.write("{}\n".format(' '.join(msgParts[1:])))
                await bot.send_message(chan, '{} Added command "{}"'.format(auMention, com2))
            else:
                await bot.send_message(chan, "{} Syntax: `!fpaddcom [command] [output]`".format(auMention))
        elif com == '!fpdelcom':
            if len(msgParts) == 2:
                if com2 in commandsList:
                    del commandsList[com2]
                    with open('commands.txt') as f:
                        lines = f.readlines()
                    with open("commands.txt", 'w', encoding='utf-8') as commandsFile:
                        for line in lines:
                            if not line.split()[0] == com2:
                                commandsFile.write("{}\n".format(line))
                    await bot.send_message(chan, '{} Removed command "{}"'.format(auMention, com2))
                else:
                    await bot.send_message(chan, '{} Command "{}" doesn{}t exist'.format(auMention, com2, "'"))
            else:
                await bot.send_message(chan, "Syntax: `!fpdelcom [command]`")
        elif com == "!fpaddincom":
            with open("incoms.txt", "a", encoding='utf-8') as incomsFile:
                incomsFile.write("{}\n".format(' '.join(msgParts[1:])))
                incomsList[com2] = ' '.join(msgParts[2:])
            await bot.send_message(chan, '{} Added in_command "{}"'.format(auMention, com2))
        elif com == '!fpdelincom':
            if com2 in incomsList:
                del incomsList[com2]
                with open('incoms.txt') as f:
                    lines = f.readlines()
                with open("incoms.txt", "w", encoding='utf-8') as incomsFile:
                    for line in lines:
                        if not line.split()[0] == com2:
                            incomsFile.write('{}\n'.format(line))
                await bot.send_message(chan, '{} Removed in_command "{}"'.format(auMention, com2))
            else:
                await bot.send_message(chan, '{} In_command "{}" doesn{}t exist'.format(auMention, com2.capitalize, "''"))
        elif com == '!fpaddmodcom':
            with open("modcoms.txt", "a", encoding="utf8") as modcomsFile:
                modcomsList[com2] = " ".join(msgParts[2:])
                modcomsFile.write("{}\n".format(' '.join(msgParts[1:])))
            await bot.send_message(chan, '{} Added mod command "{}"'.format(auMention, com2))
        elif com == '!fpdelmodcom':
            if len(msgParts) == 2:
                del modcomsList[com2]
                with open('modcoms.txt') as f:
                    lines = f.readlines()
                with open("modcoms.txt", "w", encoding="utf-8") as modcomsFile:
                    for line in lines:
                        if line:
                            if not line.split()[0].lower() == com2:
                                modcomsFile.write("{}\n".format(line))
                await bot.send_message(chan, '{} Deleted mod command "{}"'.format(auMention, com2))
        elif com == '!fpdelroles':  # Requires "Manage Roles" permission
            # Doesn't usually delete all roles at once, requires multiple executions

            roles = message.server.roles
            members = message.server.members
            # print("Roles: {}".format(len(roles)))  # Debugging
            # print("Roles: {}".format(', '.join([r.name for r in roles])))  # Debugging
            usedRoles = []
            for r in roles:
                for u in members:
                    if r in u.roles:
                        usedRoles.append(r)
                        break
            # print("Used: {}".format(', '.join([r.name for r in usedRoles])))  # Debugging
            for r in usedRoles:
                roles.remove(r)
            # print("Unused: {}".format(', '.join([r.name for r in roles])))  # Debugging
            for r in roles:
                await bot.delete_role(message.server, r)
                await bot.send_message(chan, "Deleted role {}.".format(r.name))
            await bot.send_message(chan, "Deleted unused roles.")
        elif com == '!fpreact':
            num = int(com2)
            if com3.isdigit():
                for em in bot.get_all_emojis():
                    if em.id == com3:
                        e = em
                        async for i in bot.logs_from(chan, limit=num):
                            await bot.add_reaction(i, e)
                        break
            else:
                e = com3
                try:
                    async for i in bot.logs_from(chan, limit=num):
                        await bot.add_reaction(i, e[2:-1])
                except:
                    await bot.send_message(chan, '{} Syntax: `!fpreact [messages] [emote/emote id]`'.format(auMention))
        elif com == '!fpwhitelist':
            if com2.isdigit():
                noBlockUsers.append(com2)
            else:
                await bot.send_message(chan, '{} Syntax: `!fpwhitelist [user id]`'.format(auMention))
        elif com == '!fpblacklist':
            if com2.isdigit():
                if com2 in noBlockUsers:
                    noBlockUsers.remove(com2)
                else:
                    await bot.send_message(chan, '{} {} is not whitelisted'.format(auMention, com2))
            else:
                await bot.send_message(chan, '{} Syntax: `!fpwhitelist [user id]`'.format(auMention))
                
        if com in modcomsList:
            await bot.send_message(chan, modcomsList[com])
        elif com == "!s" and len(msgParts) >= 3:
            n = int(com2)
            for i in range(n):
                await bot.send_message(chan, ' '.join(msgParts[2:]))
        elif com == "!fpgame":
            await bot.change_presence(game=discord.Game(name=' '.join(msgParts[1:])))
            await bot.send_message(chan, '{} Set game to "{}"'.format(auMention, ' '.join(msgParts[1:])))
        elif com == '!fpvoice':  # Incomplete
            if len(msgParts) >= 2:
                if com2 == 'join':
                    if len(msgParts) == 3:
                        vChannel = bot.get_channel(com3)
                    elif len(msgParts) == 2:
                        vChannel = message.author.voice_channel
                    voice = await bot.join_voice_channel(vChannel)
                    await bot.send_message(chan, 'Joined "{}" voice channel'.format(vChannel.name))
                elif com2 == 'leave':
                    for c in bot.voice_clients:
                        if c.server == message.server:
                            await voice.disconnect()
                            await bot.send_message(chan, 'Left "{}" voice channel'.format(vChannel.name))
            else:
                await bot.send_message(chan, 'Missing argument: `join`, `leave`')
        
    if userId in admins:
        if com == "!fpadduser" and len(msgParts) == 2:
            users = [str(u.id) for u in message.mentions]
            if not users:
                users = msgParts[1:]
            with open("users.txt", "a", encoding='utf-8') as userFile:
                userFile.write("{}\n".format('\n'.join(users)))
                for u in users:
                    userList.append(u)
            await bot.send_message(chan, '{} Added {} to trusted user list'.format(auMention, ', '.join(users)))
        elif com == "!fpdeluser":
            if message.mentions:
                user = message.mentions[0].id
            else:
                user = com2
            userList.remove(user)
            with open('users.txt') as f:
                lines = f.readlines()
            with open("users.txt", "w", encoding='utf-8') as userFile:
                for line in lines:
                    if line[:-1] != user:
                        userFile.write(line)
            await bot.send_message(chan, '{} Removed {} from trusted users.'.format(auMention, user))
        elif com == "!fpshutdown":
            await bot.send_message(chan, 'Shutting down client.')
            await bot.close()
            print("{} Bot shutdown.".format(currentTime()))

bot.run(token)
