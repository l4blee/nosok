import os
from pathlib import Path
from importlib import import_module
from sanic import Sanic

from sanic.log import logger


def load_blueprints(app: Sanic, path: os.PathLike) -> None:
    logger.info(f'Loading blueprints from {path}')
    for i in Path(path).glob('*.py'):
        mod = import_module(f'blueprints.{i.stem}')
        bp = mod.__dict__['bp']
        app.blueprint(bp)

    logger.info(f'Available blueprints: {list(app.blueprints.keys())}')
