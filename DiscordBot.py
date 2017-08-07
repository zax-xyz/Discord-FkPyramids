import discord
from discord.ext import commands
import time

Client = discord.Client()
bot = commands.Bot(command_prefix="!")
length = 0
last_time = 0

commands_file = open("commands.txt", "r+")
commands_list = {}
for line in commands_file:
    line_parts = line.split()
    commands_list[line_parts[0]] = " ".join(line_parts[1:])

user_file = open("users.txt", "r+")
user_list = []
for line in user_file:
    user_list.append(line[:-1])
    
incoms_file = open("incoms.txt", "r+")
incoms_list = {}
for line in incoms_file:
    incoms_list[line.split()[0]] = ' '.join(line.split()[1:])

@bot.event
async def on_ready():
    print("Bot Online!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    await bot.change_presence(game=discord.Game(name='!fphelp'))

@bot.event
async def on_message(message):
    username = str(message.author)
    user_id = username.split('#')[-1]
    msg = str(message.content).lower()
    msg_parts = msg.split()
    com = msg_parts[0]
    global length
    global py_part
    if user_id != "9044" and message.author != discord.Server.owner:
        if len(msg_parts) == 1:
            py_part = msg
            length = 1
        elif len(msg_parts) == 1 + length:
            length += 1

            for part in msg_parts:
                if part != py_part:
                    length = 0

            if length == 3:
                if time.time() - last_time >= 1000:
                    for i in [1, 2, 3, 2, 1]:
                        await bot.send_message(message.channel, "no " * i)
                    length = 0
                    last_time = time.time()
                else:
                    await bot.send_message(message.channel, "no")
                    length = 0
                    last_time = time.time()
        else:
            length = 0
    else:
        length = 0

    if com == "!pyramid" and user_id in user_list and len(msg_parts) == 3:
        p = msg_parts[2] + " "
        p_len = int(msg_parts[1]) + 1
        for i in range(1, p_len):
            await bot.send_message(message.channel, p * i)
            await asyncio.sleep(50)
        for i in range(2, p_len):
            await bot.send_message(message.channel, p * (p_len - i))
            await asyncio.sleep(50)
    elif (com == "!color" or com == "!colour") and len(msg_parts) == 2:
        if msg_parts[1].startswith("#") and len(msg_parts[1]) == 7:
            global color_hex
            color_hex = msg_parts[1][1:]
            color_role = await bot.create_role(message.channel, name="#"+color_hex, colour=discord.Colour(value=int(color_hex, 16)))
            await bot.replace_roles(message.author, color_role)
            await bot.send_message(message.channel, message.author.mention + " set colour to #" + color_hex)
    elif com in commands_list and user_id != '9044':
        await bot.send_message(message.channel, commands_list[com])
    elif com == "!fpaddcom" and user_id in user_list:
        if len(msg_parts) >= 3:
            commands_list[msg_parts[1]] = " ".join(msg_parts[2:])
            commands_file.write(' '.join(msg_parts[1:]) + "\n")
            await bot.send_message(message.channel, message.author.mention + " added command " + msg_parts[1])
        else:
            await bot.send_message(message.channel, message.author.mention + " Syntax: !fpaddcom <command> <output>")
    elif com == '!fpdelcom' and user_id in user_list:
        if len(msg_parts) == 2:
            del commands_list[msg_parts[1]]
            d = commands_file.readlines()
            commands_file.seek(0)
            for i in d:
                if not i.split()[0] == msg_parts[1]:
                    commands_file.write(i)
            commands_file.truncate()
            await bot.send_message(message.channel, message.author.mention + " removed " + msg_parts[1])
    elif com == "!fpcommands":
        await bot.send_message(message.channel, ', '.join(commands_list.keys()))
    elif com == "!s" and len(msg_parts) >= 3 and user_id in user_list:
        n = int(msg_parts[1])
        for i in range(n):
            await bot.send_message(message.channel, ' '.join(msg_parts[2:]))
            await asyncio.sleep(500)
    elif com == "!fpadduser" and user_id == "9935" and len(msg_parts) == 2:
        user_file.write(msg_parts[1] + "\n")
        user_list.append(msg_parts[1])
        await bot.send_message(message.channel, message.author.mention + ' Added #' + msg_parts[1] + ' to trusted user list')
    elif com == "!fpusers":
        await bot.send_message(message.channel, ', '.join(user_list))
    elif com == "!fpdeluser" and user_id == "9935":
        user_list.remove(msg_parts[1])
        d = user_file.readlines()
        user_file.seek(0)
        for i in d:
            if i != msg_parts[1]:
                user_file.write(i)
        user_file.truncate()
        await bot.send_message(message.channel, message.author.mention + ' Removed ' + msg_parts[1] + ' from trusted users.')
    elif com == "!fpexeca" and user_id == "9935":
        await eval(' '.join(msg_parts[1:]))
    elif com == "!fpexec" and user_id == "9935":
        exec(' '.join(msg_parts[1:]))
    elif com == "!fpgame" and user_id in user_list:
        await bot.change_presence(game=discord.Game(name=' '.join(msg_parts[1:])))
    elif com == "!fpaddincom" and user_id in user_list:
        incoms_file.write(' '.join(msg_parts[1:]) + "\n")
        incoms_list[msg_parts[1]] = ' '.join(msg_parts[2:])
        await bot.send_message(message.channel, message.author.mention + " Added in_command " + msg_parts[1])
    elif com == '!fpdelincom' and user_id in user_list:
        del incoms_list[msg_parts[1]]
        d = incoms_file.readlines()
        for i in d:
            if not i.split()[0] == msg_parts[1]:
               incoms_file.write(i)
        incoms_file.truncate()
        await bot.send_message(message.channel, message.author.mention + " Removed in_command " + msg_parts[1])
    elif com == '!fpincoms':
        await bot.send_message(message.channel, ', '.join(incoms_list.keys()))
    if user_id != '9044':
        for key in incoms_list:
            if key in msg_parts:
                await bot.send_message(message.channel, incoms_list[key])

bot.run("MzM5Mjg2NjU4MDYxMDQxNjY3.DFhyKw.RYWoaTKzRJD9nCKMJk2piCuL7J0")

