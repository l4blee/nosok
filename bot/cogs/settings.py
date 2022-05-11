from base import BASE_COLOR
from discord.ext import commands

from database import db
from utils import send_embed


class Settings(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """
        Sets prefix for the current server.
        """
        db.guilds.configs.update_one(
            {'guild_id': ctx.guild.id},
            {
                '$set': {
                    'prefix': new_prefix
                }
            },
            upsert=True
        )

        await send_embed(
            ctx=ctx,
            description=f'Prefix has been successfully changed to `{new_prefix}`',
            color=BASE_COLOR
        )

    # @commands.command(aliases=['lang'])
    async def set_language(self, ctx: commands.Context, new_lang: str):
        # TODO: check if language is available
        # possibly do it through Enum and make replies within send_embed function
        db.guilds.configs.update_one(
            {'guild_id': ctx.guild.id},
            {
                '$set': {
                    'language': new_lang
                }
            },
            upsert=True
        )

        await send_embed(
            ctx=ctx,
            description=f'Language has been successfully changed to `{new_lang}`',
            color=BASE_COLOR
        )


def setup(bot: commands.Bot):
    bot.add_cog(Settings())
