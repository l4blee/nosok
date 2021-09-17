import discord
from discord.ext import commands
from sqlalchemy import orm
import sqlalchemy as sa
import core


class Other(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context) -> None:
        pref = ctx.message.content.split(' ')[1]
        pass

        await ctx.channel.send(f'Prefix successfully changed to `{pref}`')
