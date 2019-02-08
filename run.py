import asyncio
import os
import sys
import yaml

from rfl.app import app
from rfl.utils import merge_dict


def load_config(filename):
    if not os.path.exists(filename):
        sys.exit('{} does not exist'.format(filename))
        return

    with open(filename, 'r', encoding='utf-8') as input_file:
        config = yaml.load(input_file)

    default = config.pop('default')
    config['streams'] = {
        name: merge_dict(default, stream)
        for name, stream in config['streams'].items()
    }

    return config


config = load_config('config.yaml')

loop = asyncio.get_event_loop()
loop.run_until_complete(app(config['streams']))
loop.close()