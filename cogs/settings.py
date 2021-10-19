import discord
import sqlalchemy as sa
from discord.ext import commands

import core
from base import BASE_COLOR, ERROR_COLOR, Session
from utils import send_embed
from core import (ytapi_handler as ytapi,
                  ydl_handler as ydl)


HANDLERS = {
    'YouTube API': ytapi,
    'YouTube DL': ydl
}


class Settings(commands.Cog):
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

    @commands.command(aliases=['sh'])
    async def set_handler(self, ctx: commands.Context, *handler):
        """
        Sets bot's handler for your server(YouTube API or YouTube DL one)
        """

        if not handler:
            await send_embed(
                ctx=ctx,
                description='You forgot to provide handler you want to use',
                color=ERROR_COLOR
            )
        else:
            handler = HANDLERS.get(' '.join(handler))
            if handler is None:
                await send_embed(
                    ctx=ctx,
                    description='Wrong handler provided',
                    color=ERROR_COLOR
                )

        music_cog = ctx.bot.get_cog('Music')
        q = music_cog._queues[ctx.guild.id]
        q.handler = handler
