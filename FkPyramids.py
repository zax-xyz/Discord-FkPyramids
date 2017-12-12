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
vc_count = 0
vc_queue = [filename for filename in os.listdir('Music')]
commands_list = {}
incoms_list = {}
modcoms_list = {}
regmodcoms = ["!pyramid", '!fpaddcom', '!fpdelcom', '!fpaddincom', '!fpdelincom', '!fpaddmodcom', '!fpdelmodcom', '!fpreact', '!s', '!fpgame', '!fpreact', '!fpwhitelist']
admins = ['135678905028706304']
noblock_users = ['339286658061041667']
x = 0
cooldown = 0

with open("commands.txt", "r", encoding="utf-8") as commands_file, open("users.txt", "r", encoding='utf-8') as user_file, open("incoms.txt", "r", encoding='utf-8') as incoms_file, open("modcoms.txt", "r", encoding='utf-8') as modcoms_file, open("token.txt", 'r') as token_file:
    for line in commands_file:
        line_parts = line.split()
        try:
            commands_list[line_parts[0].lower()] = " ".join(line_parts[1:])
        except:
            pass
    user_list = [line[:-1] for line in user_file]
    for line in incoms_file:
        line_parts = line.split()
        try:
            incoms_list[line_parts[0].lower()] = ' '.join(line_parts[1:])
        except:
            pass
    for line in modcoms_file:
        line_parts = line.split()
        try:
            modcoms_list[line_parts[0].lower()] = ' '.join(line_parts[1:])
        except:
            pass
    token = token_file.readline()[:-1]


@bot.event
async def on_ready():
    print("{} Bot Online".format("{:%H:%M:%S} ".format(datetime.datetime.now())))
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

@bot.event
async def on_message(message):
    global x
    global vc_count
    global vc
    global v_channel
    global au_mention
    global user_id
    global chan
    global cooldown
    global player
    username = str(message.author)
    au_mention = message.author.mention
    user_id = message.author.id
    msg = str(message.content)
    msg_parts = msg.split()
    chan = message.channel
    print('{} {}: {}'.format("{:%H:%M:%S} ".format(datetime.datetime.now()), username, msg))
    try:
        com = msg_parts[0].lower()
    except:
        com = None
        pass
    try:
        com2 = msg_parts[1].lower()
    except:
        com2 = None
        pass
    try:
        com3 = msg_parts[2]
    except:
        com3 = None
        pass
    global length
    global py_part
    if user_id not in noblock_users:
        if message.author.id != message.server.owner.id:
            if len(msg_parts) == 1:
                if len(msg_parts) == length - 1 and msg == py_part:
                    await bot.send_message(chan, "Baby pyramids don't count, you fucking degenerate. {}".format(au_mention))
                py_part = msg
                length = 1
            elif len(msg_parts) == 1 + length:
                length += 1
                for part in msg_parts:
                    if part != py_part:
                        length = 0
                if length == 3:
                    length = 0
                    for i in [1,2,3,2,1]:
                        await bot.send_message(chan, "no " * i)
            else:
                length = 0
        else:
            length = 0

    if user_id != '339286658061041667':
        if com in commands_list:
            await bot.send_message(chan, commands_list[com])
        elif time.time() - cooldown > 30:
            for key in incoms_list:
                if key in msg.lower():
                    await bot.send_message(chan, incoms_list[key])
                    break
            cooldown = time.time()
                
        if (com == "!color" or com == "!colour") and message.server.id == "311016926925029376":
            if ((com2.startswith("#") and len(com2) == 7) or len(com2)) == 6 and len(msg_parts) == 2:
                if len(com2) == 7:
                    color_hex = com2[1:]
                else:
                    color_hex = com2
                await bot.send_message(chan, "{} Setting color to #{}".format(au_mention, color_hex))
                for r in message.author.roles:
                    if r.name.startswith('#'):
                        await bot.remove_roles(message.author, r)
                for r in message.server.roles:
                    if r.name == '#{}'.format(color_hex):
                        await bot.add_roles(message.author, r)
                        break
                else:
                    color_role = await bot.create_role(message.server, name="#{}".format(color_hex), colour=discord.Colour(value=int(color_hex, 16)))
                    await bot.move_role(message.server, color_role, len(message.server.roles)-8)
                    await bot.add_roles(message.author, color_role)
                await bot.send_message(chan, "{} Set colour to #{}".format(au_mention, color_hex))
            else:
                await bot.send_message(chan, "{} Syntax: `{} [{} hex code]`".format(au_mention, com, com[1:]))

    if user_id in user_list or user_id in admins:
        if com == "!pyramid" and len(msg_parts) >= 3:
            p = "{} ".format(' '.join(msg_parts[2:]))
            p_len = int(com2) + 1
            for i in range(1, p_len):
                await bot.send_message(chan, p * i)
            for i in range(2, p_len):
                await bot.send_message(chan, p * (p_len - i))
        elif com == "!delmsg":
            if com2.isdigit():
                com2 = int(com2)
                async for m in bot.logs_from(chan, com2):
                    await bot.delete_message(m)
        elif com == "!fpaddcom":
            if len(msg_parts) >= 3:
                with open("commands.txt", "a", encoding="utf-8") as commands_file:
                    commands_list[com2] = " ".join(msg_parts[2:])
                    commands_file.write("{}\n".format(' '.join(msg_parts[1:])))
                await bot.send_message(chan, '{} Added command "{}"'.format(au_mention, com2))
            else:
                await bot.send_message(chan, "{} Syntax: `!fpaddcom [command] [output]`".format(au_mention))
        elif com == '!fpdelcom':
            if len(msg_parts) == 2:
                if com2 in commands_list:
                    del commands_list[com2]
                    with open('commands.txt') as f:
                        lines = f.readlines()
                    with open("commands.txt", 'w', encoding='utf-8') as commands_file:
                        for line in lines:
                            if not line.split()[0] == com2:
                                commands_file.write("{}\n".format(line))
                    await bot.send_message(chan, '{} Removed command "{}"'.format(au_mention, com2))
                else:
                    await bot.send_message(chan, '{} Command "{}" doesn{}t exist'.format(au_mention, com2, "'"))
            else:
                await bot.send_message(chan, "Syntax: `!fpdelcom [command]`")
        elif com == "!fpaddincom":
            with open("incoms.txt", "a", encoding='utf-8') as incoms_file:
                incoms_file.write("{}\n".format(' '.join(msg_parts[1:])))
                incoms_list[com2] = ' '.join(msg_parts[2:])
            await bot.send_message(chan, '{} Added in_command "{}"'.format(au_mention, com2))
        elif com == '!fpdelincom':
            if com2 in incoms_list:
                del incoms_list[com2]
                with open('incoms.txt') as f:
                    lines = f.readlines()
                with open("incoms.txt", "w", encoding='utf-8') as incoms_file:
                    for line in lines:
                        if not line.split()[0] == com2:
                            incoms_file.write('{}\n'.format(line))
                await bot.send_message(chan, '{} Removed in_command "{}"'.format(au_mention, com2))
            else:
                await bot.send_message(chan, '{} In_command "{}" doesn{}t exist'.format(au_mention, com2.capitalize, "''"))
        elif com == '!fpaddmodcom':
            with open("modcoms.txt", "a", encoding="utf8") as modcoms_file:
                modcoms_list[com2] = " ".join(msg_parts[2:])
                modcoms_file.write("{}\n".format(' '.join(msg_parts[1:])))
            await bot.send_message(chan, '{} Added mod command "{}"'.format(au_mention, com2))
        elif com == '!fpdelmodcom':
            if len(msg_parts) == 2:
                del modcoms_list[com2]
                with open('modcoms.txt') as f:
                    lines = f.readlines()
                with open("modcoms.txt", "w", encoding="utf-8") as modcoms_file:
                    for line in lines:
                        if line:
                            if not line.split()[0].lower() == com2:
                                modcoms_file.write("{}\n".format(line))
                await bot.send_message(chan, '{} Deleted mod command "{}"'.format(au_mention, com2))
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
        elif com == '!fpreact' and user_id in user_list:
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
                    await bot.send_message(chan, '{} Syntax: `!fpreact [emote/emote id]`'.format(au_mention))
        elif com == '!fpwhitelist':
            if com2.isdigit():
                noblock_users.append(int(com2))
            else:
                await bot.send_message(chan, '{} Syntax: `!fpwhitelist [user id]`'.format(au_mention))
                
        if com in modcoms_list:
            await bot.send_message(chan, modcoms_list[com])
        
        elif com == "!s" and len(msg_parts) >= 3:
            n = int(com2)
            for i in range(n):
                await bot.send_message(chan, ' '.join(msg_parts[2:]))
                await asyncio.sleep(1)
        elif com == "!fpgame":
            await bot.change_presence(game=discord.Game(name=' '.join(msg_parts[1:])))
            await bot.send_message(chan, '{} Set game to "{}"'.format(au_mention, ' '.join(msg_parts[1:])))
            
        elif com == '!fpvoice':
            if len(msg_parts) >= 2:
                if com2 == 'join':
                    if len(msg_parts) == 3:
                        v_channel = bot.get_channel(com3)
                    elif len(msg_parts) == 2:
                        v_channel = message.author.voice_channel
                    vc = await bot.join_voice_channel(v_channel)
                    await bot.send_message(chan, 'Joined "{}" voice channel'.format(v_channel.name))
                elif com2 == 'play':
                    player = vc.create_ffmpeg_player("Music/{}".format(vc_queue[vc_count % len(vc_queue)]))
                    player.start
                    vc_count += 1
                elif com2 == 'leave':
                    for c in bot.voice_clients:
                        if c.server == message.server:
                            await vc.disconnect()
                            await bot.send_message(chan, 'Left "{}" voice channel'.format(v_channel.name))
            else:
                await bot.send_message(chan, 'Missing argument. `join`, `play`, `leave`')
        
    if user_id in admins:
        if com == "!fpadduser" and len(msg_parts) == 2:
            users = [str(u.discriminator) for u in message.mentions]
            if not users:
                users = msg_parts[1:]
            with open("users.txt", "a", encoding='utf-8') as user_file:
                user_file.write("{}".format('\n'.join(users)))
                user_list.append('\n'.join(users))
            await bot.send_message(chan, '{} Added {} to trusted user list'.format(au_mention, ', '.join(users)))
        elif com == "!fpdeluser":
            if message.mentions:
                user = message.mentions[0].id
            else:
                user = com2
            user_list.remove(user)
            with open('users.txt') as f:
                lines = f.readlines()
            with open("users.txt", "w", encoding='utf-8') as user_file:
                for line in lines:
                    if line != user:
                        user_file.write(line)
            await bot.send_message(chan, '{} Removed {} from trusted users.'.format(au_mention, user))

    await bot.process_commands(message)


@bot.command()
async def fpcommands():
    await bot.say("{} Commands are: {}".format(au_mention, ', '.join(commands_list.keys())))

@bot.command()
async def fpusers():
    await bot.say("{} Authorised users are: {}".format(au_mention, ', '.join(user_list)))

@bot.command()
async def fpincoms():
    await bot.say("{} In_commands are: {}".format(au_mention, ', '.join(incoms_list.keys())))

@bot.command()
async def fpmodcoms():
    await bot.say("{} Mod commands are: {}, {}".format(au_mention, ', '.join(modcoms_list), ', '.join(regmodcoms)))

@bot.command()
async def nobully():
    nobully_embed = discord.Embed(description="**Don't Bully!**")
    nobully_embed.set_image(url="https://i.imgur.com/jv7O5aj.gif")
    await bot.say(embed=nobully_embed)

"""
@bot.command()
async def fpavatar(id):
    if id.isdigit():
        user = bot.get_user_info(id)
        await bot.say(user.avatar_url)
"""

bot.run(token)
