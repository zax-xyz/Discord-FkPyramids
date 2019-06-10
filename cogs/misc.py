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

import json
import random

import discord
from discord.ext import commands


def from_guild():
    def predicate(ctx):
        return ctx.message.guild == ctx.bot.get_guild(311016926925029376)
    return commands.check(predicate)


def is_mod():
    def predicate(ctx):
        return ctx.bot._is_mod(ctx.author.id)
    return commands.check(predicate)


class Misc(commands.Cog):

    """Miscellaneous commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bully"])
    async def nobully(self, ctx):
        """
        Don't bully!

        Returns gif of Anti-Bully Ranger Akari Akaza
        (I'll kill you so hard you will die to death)
        """
        embed = discord.Embed(description="**Don't Bully!**")
        embed.set_image(url="https://fp.zaxu.tk/NoBully.gif")
        await ctx.send(embed=embed)

    @commands.command(aliases=["color"])
    @from_guild()
    async def colour(self, ctx, colour_hex: str):
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

    def _get_quote(self, search):
        with open("gxquotes.json") as f:
            quotes = json.load(f)

        try:
            index = int(search)
        except TypeError:
            quote = random.choice(quotes)
            index = quotes.index(quote) + 1
        except ValueError:
            words = search.lower().split()
            matches = [q for q in quotes if all(w in q.lower() for w in words)]

            if not matches:
                return None, None

            quote = random.choice(matches)
            index = quotes.index(quote) + 1
        else:
            try:
                quote = quotes[index - 1]
            except IndexError:
                return None, None

        return quote, index

    @commands.group(aliases=["gx_quote", "gx-quote"])
    async def gxquote(self, ctx):
        """
        Get random quote from gxmwp.

        If no valid subcommand is passed, the string passed is used to search
        through which quotes contain all the keywords given and returns a
        random quote which matches the search.
        If an integer is passed, the quote at that index is returned.
        """
        if ctx.invoked_subcommand is None:
            quote, index = self._get_quote(ctx.subcommand_passed)
            if quote is None:
                embed = self.bot.error_embed(
                    ctx,
                    title="Error in command `gxquote`",
                    description="No quote found."
                )
                return await ctx.send(embed=embed)

            embed = self.bot.create_embed(ctx, title=f"Quote {index}",
                                          description=quote)
            await ctx.send(embed=embed)

    @gxquote.command(name="list")
    async def _list(self, ctx):
        """List quotes"""
        embed = self.bot.create_embed(
            ctx,
            title="Quote list",
            description="https://zaxu.tk/gxquotes"
        )
        await ctx.send(embed=embed)

    @gxquote.command()
    @is_mod()
    async def add(self, ctx, *, quote: str):
        """Add quote"""
        with open("gxquotes.json") as f:
            quotes = json.load(f)

        quotes.append(quote)

        with open("gxquotes.json", "w") as f:
            json.dump(quotes, f, indent=2)

        embed = self.bot.create_embed(
            ctx,
            title="Added quote",
            description=f"Added quote at index {len(quotes)}"
        )
        await ctx.send(embed=embed)

    @gxquote.command()
    @is_mod()
    async def delete(self, ctx, index: int):
        """Delete quote"""
        with open("gxquotes.json") as f:
            quotes = json.load(f)

        del quotes[index - 1]

        with open("gxquotes.json", "w") as f:
            json.dump(quotes, f, indent=2)

        embed = self.bot.create_embed(
            ctx,
            title="Removed quote",
            description=f"Removed quote {index}"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["user", "user_info", "user-info"])
    async def userinfo(self, ctx, user: discord.Member):
        """Returns information about a user."""
        embed = discord.Embed()
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(name="Display name", value=user.display_name)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Colour", value=str(user.colour).upper())
        embed.add_field(
            name="Server join date",
            value=user.joined_at.strftime("%b %-d %Y %-H:%M (UTC)")
        )
        embed.add_field(
            name="Account creation date",
            value=user.created_at.strftime("%b %-d %Y %-H:%M (UTC)")
        )
        embed.add_field(
            name="Socioeconomic status",
            value="Rich" if user.is_avatar_animated() else "Probably broke"
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
