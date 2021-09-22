import discord
import sqlalchemy as sa
from discord.ext import commands

import core
from base import BASE_COLOR


class Other(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context):
        with core.Session.begin() as s:
            res = s.query(core.Config).filter_by(guild_id=ctx.guild.id).first()
            pref = ctx.message.content.split(' ')[1]
            if res is None:
                s.execute(sa.insert(core.Config).
                          values(guild_id=ctx.guild.id, prefix=pref))
            else:
                s.execute(sa.update(core.Config).
                          where(core.Config.guild_id == ctx.guild.id).
                          values(prefix=pref))

            embed = discord.Embed(description=f'Prefix has been successfully changed to `{pref}`',
                                  color=BASE_COLOR)
            await ctx.channel.send(embed=embed)
