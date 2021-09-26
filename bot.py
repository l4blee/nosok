import discord
from discord.ext import commands

from base import BASE_PREFIX
import core


Session = core.Session


def get_prefix(_, msg: discord.Message) -> str:
    with Session.begin() as s:
        res = s.query(core.Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


class MusicBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)


bot: MusicBot = MusicBot(get_prefix)
