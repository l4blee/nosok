from .external import *
from commands import utils
from .music import *


CMDS_BY_TYPES = {
    'commands': (
        'help',
        'set_prefix'
    ),
    'music': (
        'play',
        'join',
        'leave',
        'stop',
        'search',
        'queue',
        'repeat',
        'pause',
        'resume',
        'clear',
        'skip',
        'volume',
        'remove'
    )
}

CMDS = set()
for i in CMDS_BY_TYPES.values():
    CMDS = CMDS.union(i)
