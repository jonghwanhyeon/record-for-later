import asyncio
import os
import subprocess
import sys
import yaml

from rfl.app import app
from rfl.utils import merge_dict

owner_exists = ('UID' in os.environ) and ('GID' in os.environ)

def load_config(filename):
    if not os.path.exists(filename):
        sys.exit('{} does not exist'.format(filename))
        return

    with open(filename, 'r', encoding='utf-8') as input_file:
        config = yaml.full_load(input_file)

    default = config.pop('default')
    config['streams'] = {
        name: merge_dict(default, stream)
        for name, stream in config['streams'].items()
    }

    return config

if __name__ == '__main__':
    if owner_exists:
        uid, gid = int(os.environ['GID']), int(os.environ['UID'])
        subprocess.run(['chown', f'{uid}:{gid}', '/rfl/config.yaml'])
        subprocess.run(['chown', f'{uid}:{gid}', '/rfl/streams'])
 
        os.setgid(gid)
        os.setuid(uid)

    config = load_config('config.yaml')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app(config['streams']))
    loop.close()
