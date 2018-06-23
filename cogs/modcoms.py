import discord
from discord.ext import commands
from termcolor import colored
import json

import global_settings as gvars


class Mod_Commands:
    def __init__(self, bot):
        self.bot = bot


    def __global_check(self, ctx):
        return ctx.message.author.id in gvars.mods or commands.is_owner()


    @commands.command(brief="Creates pyramids.")
    async def pyramid(self, ctx, length: int, *, message: str):
        message += ' '
        for i in [length - abs(i) for i in range(-length + 1, length)]:
            await ctx.send(message * i)


    @commands.command(brief="Deletes messages.")
    async def delmsg(self, ctx, n: int):
        # Requires "Manage Messages" permission
        async for m in ctx.message.channel.history(limit=n):
            try:
                await m.delete()
            except discord.errors.Forbidden:
                print("Insufficient permissions")


    @commands.command(brief="Adds a command.")
    async def addcom(self, ctx, command: str, *, output: str):
        gvars.commands[command] = output

        with open('commands.json', 'w', encoding='utf-8') as commandsFile:
            json.dump(gvars.commands, commandsFile)

        await send_mention(ctx, f'Added command "{command}"')


    @commands.command(brief="Deletes command.")
    async def delcom(self, ctx, command: str):
        if command in gvars.commands:
            del gvars.commands[command]

            with open('commands.json', 'w', encoding='utf-8') as commandsFile:
                json.dump(gvars.commands, commandsFile)

            await send_mention(ctx, f'Removed command "{command}"')
        else:
            await send_mention(ctx, f'Command "{command}" doesn\'t exist')


    @commands.command(brief="Adds in_command.")
    async def addincom(self, ctx, in_com: str, *, output: str):
        gvars.incoms[in_com] = output

        with open("incoms.json", "w", encoding="utf-8") as incomsFile:
            json.dump(gvars.incoms, incomsFile)

        await send_mention(ctx, f'Added in_command "{in_com}"')


    @commands.command(brief="Deletes in_command.")
    async def delincom(self, ctx, in_com: str):
        if in_com in gvars.incoms:
            del gvars.incoms[in_command]

            with open("incoms.json", "w", encoding="utf-8") as incomsFile:
                json.dump(gvars.incoms, incomsFile)

            await send_mention(ctx, f'Removed in_command "{in_com}"')
        else:
            await send_mention(ctx, f'In_command "{in_com}" doesn\'t exist')


    @commands.command(brief="Add mod commmand.")
    async def addmodcom(self, ctx, command: str, *, output: str):
        gvars.modComs[command] = output

        with open("modcoms.json", "w", encoding="utf-8") as modcomsFile:
            json.dump(gvars.modComs, modcomsFile)

        await channel.send(f'{mention} Added mod command "{command}"')


    @commands.command(brief="Delete mod command.")
    async def delmodcom(self, ctx, command: str):
        if modcom in gvars.modComs:
            del gvars.modComs[command]

            with open("modcoms.json", "w", encoding="utf-8") as modcomsFile:
                json.dump(gvars.modComs, modcomsFile)

            await send_mention(ctx, f'Deleted mod command "{command}"')
        else:
            send_mention(ctx, f'Mod command "{command}" doesn\'t exist')


    @commands.command(brief="Delete all unused roles in server.")
    async def delroles(self, ctx):
        # Requires "Manage Roles" permission.

        unused_roles = filter(lambda r: not r.members, ctx.message.guild.roles)

        for r in list(unused_roles):
            await r.delete()
            await ctx.send(f'Deleted role "{r.name}".')

        await ctx.send("Deleted unused roles.")


    @commands.command(brief="Add reaction to last [n] messages in channel.")
    async def react(self, ctx, n: int, em: str):
        if em.isdigit():
            # Get emoji by ID
            em = discord.utils.get(bot.emojis(), id=int(em))

            if em:
                async for i in ctx.history(limit=n):
                    await i.add_reaction(em)
            else:
                await send_mention(ctx, 'Could not find emote')
        else:
            # Get emoji directly using string
            try:
                async for i in ctx.history(limit=n):
                    await i.add_reaction(em[2:-1])
            except (discord.errors.NotFound, discord.errors.InvalidArgument):
                await send_mention(ctx, 'Usage: `!fpreact [n] [emote]`')
            except discord.errors.Forbidden:
                await send_mention(ctx, 'Could not react to message.')


    @commands.command(brief="Whitelist user from pyramid blocking.")
    async def whitelist(self, ctx, user: int):
        gvars.noBlockUsers.append(user)


    @commands.command(brief="Remove user from pyramid blocking whitelist.")
    async def blacklist(self, ctx, user: int):
        if user in noBlockUsers:
            gvars.noBlockUsers.remove(user)
        else:
            await send_mention(ctx, f'{user} is not whitelisted')


    @commands.command(brief="Send message [n] amount of times in a row.")
    async def s(self, ctx, n: int, message: str):
        for i in range(n):
            await ctx.send(message)


    @commands.command(brief="Change activity status of bot.")
    async def status(self, ctx, aType: str, *, name: str):
        types = {'playing': 1, 'listening': 2, 'watching': 3}

        if aType in types:
            aType = types[aType]
        else:
            return await send_mention(ctx, 'Invalid type')

        await bot.change_presence(activity=discord.Activity(name=name, type=aType))
        await send_mention(ctx, f'Set activity to "{name}"')


def setup(bot):
    bot.add_cog(Mod_Commands(bot))
