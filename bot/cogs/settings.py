from base import BASE_COLOR
from discord.ext import commands
from orm.base import db
from orm.models import GuildConfig
from utils import send_embed


class Settings(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """
        Sets prefix for the current server.
        """
        with db.atomic():
            res = GuildConfig.get_or_none(GuildConfig.guild_id == ctx.guild.id)
            if res is None:
                GuildConfig\
                    .insert(guild_id=ctx.guild.id, prefix=new_prefix)\
                    .execute()
            else:
                GuildConfig\
                    .update({GuildConfig.prefix: new_prefix})\
                    .where(GuildConfig.guild_id == ctx.guild.id)\
                    .execute()

        await send_embed(
            ctx=ctx,
            description=f'Prefix has been successfully changed to `{new_prefix}`',
            color=BASE_COLOR
        )
