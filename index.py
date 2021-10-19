from discord import Message

from base import Base, Session, BASE_PREFIX
from core import MusicBot, Config


def get_prefix(_, msg: Message) -> str:
    with Session.begin() as s:
        res = s.query(Config).filter_by(guild_id=msg.guild.id).first()
        return res.prefix if res is not None else BASE_PREFIX


Base.metadata.create_all()

bot = MusicBot(get_prefix)
bot.run()
