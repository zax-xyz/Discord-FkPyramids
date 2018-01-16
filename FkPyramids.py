import discord
from discord.ext import commands
import asyncio
import os
import datetime
import time


if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so.0.6.1')

Client = discord.Client()
bot = commands.Bot(command_prefix="!")
length = 0
vcCount = 0
vcQueue = [filename for filename in os.listdir('Music')]
commandsList = {}
incomsList = {}
modcomsList = {}
regmodcoms = ["!pyramid", '!fpaddcom', '!fpdelcom', '!fpaddincom', '!fpdelincom', '!fpaddmodcom', '!fpdelmodcom', '!fpreact', '!s', '!fpgame', '!fpreact', '!fpwhitelist']
admins = ['135678905028706304']
noblockUsers = ['339286658061041667']
x = 0
cooldown = 0

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

async def pyNum():
    for i in [1,2,3,2,1]:
        yield i

@bot.event
async def on_ready():
    print("{} Bot Online".format("{:%H:%M:%S} ".format(datetime.datetime.now())))
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

@bot.event
async def on_message(message):
    global x
    global vcCount
    global voice
    global vChannel
    global auMention
    global userId
    global chan
    global cooldown
    global player
    username = str(message.author)
    auMention = message.author.mention
    userId = message.author.id
    msg = str(message.content)
    msgParts = msg.split()
    chan = message.channel
    print('{} {}: {}'.format("{:%H:%M:%S} ".format(datetime.datetime.now()), username, msg))
    try:
        com = msgParts[0].lower()
    except:
        com = None
        pass
    try:
        com2 = msgParts[1].lower()
    except:
        com2 = None
        pass
    try:
        com3 = msgParts[2]
    except:
        com3 = None
        pass
    global length
    global pyPart
    if chan.is_private:
        if userId != '339286658061041667':
            if len(msgParts) == 1:
                if len(msgParts) == length - 1 and msg == pyPart:
                    await bot.send_message(chan, "Baby pyramids don't count, you fucking degenerate. {}".format(auMention))
                pyPart = msg
                length = 1
            elif len(msgParts) == 1 + length:
                length += 1
                for part in msgParts:
                    if part != pyPart:
                        length = 0
                if length == 3:
                    length = 0
                    await bot.send_message(chan, "no")
            else:
                length = 0
        else:
            length = 0
        if userId == '135678905028706304':
            if com == '!send':
                if len(msgParts) >= 3:
                    await bot.send_message(bot.get_channel(com2), ' '.join(msgParts[2:]))
    else:
        if userId not in noblockUsers and userId != message.server.owner.id:
            if len(msgParts) == 1:
                if len(msgParts) == length - 1 and msg == pyPart:
                    await bot.send_message(chan, "Baby pyramids don't count, you fucking degenerate. {}".format(auMention))
                pyPart = msg
                length = 1
            elif len(msgParts) == 1 + length:
                length += 1
                for part in msgParts:
                    if part != pyPart:
                        length = 0
                if length == 3:
                    length = 0
                    async for i in pyNum():
                        await bot.send_message(chan, "no " * i)
            else:
                length = 0
        else:
            length = 0

    if userId != '339286658061041667':
        if com in commandsList:
            await bot.send_message(chan, commandsList[com])
        elif time.time() - cooldown > 30:
            for key in incomsList:
                if key in msg.lower():
                    await bot.send_message(chan, incomsList[key])
                    break
            cooldown = time.time()
                
        if (com == "!color" or com == "!colour") and message.server.id == "311016926925029376":
            if ((com2.startswith("#") and len(com2) == 7) or len(com2)) == 6 and len(msgParts) == 2:
                if len(com2) == 7:
                    colorHex = com2[1:]
                else:
                    colorHex = com2
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

    if userId in userList or userId in admins:
        if com == "!pyramid" and len(msgParts) >= 3:
            p = "{} ".format(' '.join(msgParts[2:]))
            pLen = int(com2) + 1
            for i in range(1, pLen):
                await bot.send_message(chan, p * i)
            for i in range(2, pLen):
                await bot.send_message(chan, p * (pLen - i))
        elif com == "!delmsg":
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
        elif com == '!fpdelroles':  # doesn't work
            roles = message.server.roles
            members = message.server.members
            for r in roles:
                for u in members:
                    if r in u.roles:
                        await bot.delete_role(message.server, r)
                        await bot.send_message(chan, "Deleted role {}.".format(r.name))
                        break
                    
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
                noblockUsers.append(com2)
            else:
                await bot.send_message(chan, '{} Syntax: `!fpwhitelist [user id]`'.format(auMention))
        elif com == '!fpblacklist':
            if com2.isdigit():
                if com2 in noblockUsers:
                    noblockUsers.remove(com2)
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
                await asyncio.sleep(1)
        elif com == "!fpgame":
            await bot.change_presence(game=discord.Game(name=' '.join(msgParts[1:])))
            await bot.send_message(chan, '{} Set game to "{}"'.format(auMention, ' '.join(msgParts[1:])))
            
        elif com == '!fpvoice':
            if len(msgParts) >= 2:
                if com2 == 'join':
                    if len(msgParts) == 3:
                        vChannel = bot.get_channel(com3)
                    elif len(msgParts) == 2:
                        vChannel = message.author.voice_channel
                    voice = await bot.join_voice_channel(vChannel)
                    await bot.send_message(chan, 'Joined "{}" voice channel'.format(vChannel.name))
                elif com2 == 'play':
                    player = voice.create_ffmpeg_player("Music/We Are Number One but it's the Night of Nights.mp3")
                    player.start
                elif com2 == 'leave':
                    for c in bot.voice_clients:
                        if c.server == message.server:
                            await voice.disconnect()
                            await bot.send_message(chan, 'Left "{}" voice channel'.format(vChannel.name))
                elif com2 == 'test':
                    voice = await bot.join_voice_channel(vChannel)
                    player = voice.create_ffmpeg_player("We Are Number One but it's the Night of Nights.mp3")
                    player.start
            else:
                await bot.send_message(chan, 'Missing argument: `join`, `play`, `leave`')
        
    if userId in admins:
        if com == "!fpadduser" and len(msgParts) == 2:
            users = [str(u.id) for u in message.mentions]
            if not users:
                users = msgParts[1:]
            with open("users.txt", "a", encoding='utf-8') as userFile:
                userFile.write("{}\n".format('\n'.join(users)))
                userList.append('\n'.join(users))  # fix later
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

    await bot.process_commands(message)


@bot.command()
async def fpcommands():
    await bot.say("{} Commands are: {}".format(auMention, ', '.join(commandsList.keys())))

@bot.command()
async def fpusers():
    await bot.say("{} Authorised users are: {}".format(auMention, ', '.join(userList)))

@bot.command()
async def fpincoms():
    await bot.say("{} In_commands are: {}".format(auMention, ', '.join(incomsList.keys())))

@bot.command()
async def fpmodcoms():
    await bot.say("{} Mod commands are: {}, {}".format(auMention, ', '.join(modcomsList), ', '.join(regmodcoms)))

@bot.command()
async def nobully():
    nobullyEmbed = discord.Embed(description="**Don't Bully!**")
    nobullyEmbed.set_image(url="https://i.imgur.com/jv7O5aj.gif")
    await bot.say(embed=nobullyEmbed)

"""
@bot.command()
async def fpavatar(id):
    if id.isdigit():
        user = bot.get_user_info(id)
        await bot.say(user.avatar_url)
"""

bot.run(token)
