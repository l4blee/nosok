from json import load


def get_prefix(msg):
    id = msg.guild.id
    with open('config/servers.json', 'r') as file:
        cfg = load(file)
        if str(id) in cfg.keys() and 'prefix' in cfg[str(id)]:
            return cfg[str(id)]['prefix']
        else:
            return '!'
