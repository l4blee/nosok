from base import BASE_COLOR
from discord.ext import commands

import exceptions
from database import db
from languages import LOCALES, get_phrase
from utils import send_embed


class Settings(commands.Cog):
    @commands.command(aliases=['sp'])
    async def set_prefix(self, ctx: commands.Context, new_prefix: str):
        """
        Sets prefix for the current guild.
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
            description=await get_phrase(ctx, 'prefix_set') % dict(new_prefix=new_prefix),
            color=BASE_COLOR
        )

    @commands.command(aliases=['lang', 'setl', 'setloc', 'set_loc'])
    async def set_language(self, ctx: commands.Context, new_lang: str):
        """
        Sets language for the current guild.
        """
        if new_lang not in LOCALES:
            raise exceptions.WrongLocale
            return

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
            description=await get_phrase(ctx, 'language_set') % dict(new_lang=new_lang),
            color=BASE_COLOR
        )


def setup(bot: commands.Bot):
    bot.add_cog(Settings())
