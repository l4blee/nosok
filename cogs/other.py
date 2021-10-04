import discord
import sqlalchemy as sa
from discord.ext import commands

import core
from base import BASE_COLOR, Session


class Other(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """
        Sets prefix for the current server.
        """
        with Session.begin() as s:
            res = s.query(core.Config).filter_by(guild_id=ctx.guild.id).first()
            if res is None:
                s.execute(sa.insert(core.Config).
                          values(guild_id=ctx.guild.id, prefix=new_prefix))
            else:
                s.execute(sa.update(core.Config).
                          where(core.Config.guild_id == ctx.guild.id).
                          values(prefix=new_prefix))

            embed = discord.Embed(description=f'Prefix has been successfully changed to `{new_prefix}`',
                                  color=BASE_COLOR)
            await ctx.channel.send(embed=embed)
