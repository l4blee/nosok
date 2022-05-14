import json
from pathlib import Path

from discord.ext import commands

from database import db

LOCALES = {}
for i in Path('bot/translated/').glob('*.json'):
        with open(i.absolute(), encoding='utf-8') as f:
            LOCALES[i.stem] = json.load(f)


async def get_phrase(ctx: commands.Context, key: str) -> str:
    global LOCALES

    lang = await db.get_language(ctx)
    if lang not in LOCALES:
        return LOCALES['EN'][key]

    return LOCALES[lang][key]
