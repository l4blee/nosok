from .external import *
from commands import utils
from .music import *

CMDS_BY_TYPES = {
    'commands': (
        'help',
        'set_prefix'
    ),
    'music': filter(lambda s: not s.startswith('_'), music.__dict__)
}

CMDS = set()
for i in CMDS_BY_TYPES.values():
    CMDS = CMDS.union(i)
