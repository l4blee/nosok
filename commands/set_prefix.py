import json


async def main(argv, msg):
    new_prefix = argv[0]
    guild_id = msg.guild.id
    with open('./config/servers.json', 'r') as f:
        cfg = json.load(f)

    cfg[str(guild_id)] = dict() if guild_id not in cfg.keys() else cfg[str(guild_id)]
    cfg[str(guild_id)]['prefix'] = new_prefix
    with open('./config/servers.json', 'w') as f:
        json.dump(cfg, f, indent=4)

    await msg.channel.send(f'Prefix has been successfully changed to `{new_prefix}`')
