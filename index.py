import os
from importlib import import_module
from pathlib import Path

from discord_components import DiscordComponents

from base import Base
from core import bot

Base.metadata.create_all()


# for cls in [import_module(f'cogs.{i.stem}').__dict__[i.stem.title()] for i in Path('./cogs/').glob('*.py')]:
#     exec(f'{cls.__name__.lower()} = cls()')
#     bot.add_cog(eval(cls.__name__.lower()))


bot.run()
