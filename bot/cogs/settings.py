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
        await db.set_prefix(ctx, new_prefix)

        await send_embed(
            ctx=ctx,
            description=f'Prefix has been successfully changed to `{new_prefix}`',
            color=BASE_COLOR
        )
