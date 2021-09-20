from discord.ext import commands
import sqlalchemy as sa
import core


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

            await ctx.channel.send('Prefix has been successfully changed to `%s`' % pref)
