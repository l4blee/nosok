import json
from pathlib import Path

from discord.ext import commands

from database import db

LOCALES = {}
for i in Path('bot/translated/').glob('*.json'):
    with open(i.absolute(), encoding='utf-8') as f:
        LOCALES[i.stem.lower()] = json.load(f)


async def get_phrase(ctx: commands.Context, key: str) -> str:
    global LOCALES

    lang = await db.get_language(ctx)
    lang = lang.lower()
    if lang not in LOCALES:
        return LOCALES['en'][key]

    try:
        return LOCALES[lang][key]
    except KeyError:
        return LOCALES['en'][key]
