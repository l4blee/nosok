from json import load


def get_prefix(msg):
    id = msg.guild.id
    with open('config/servers.json', 'r') as file:
        cfg = load(file)
        if str(id) in cfg.keys() and 'prefix' in cfg[str(id)]:
            return cfg[str(id)]['prefix']
        else:
            return '!'


def get_voice_instance(msg, client):
    if not client.voice_clients:
        return None

    id = msg.guild.id
    for cli in client.voice_clients:
        if cli.guild.id == id:
            return cli
    else:
        return None
