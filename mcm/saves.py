"""
used for uh
we'll see
code hard
"""

import json
from pathlib import Path

def get_saves():
    """
    load saves from config file
    """
    if not Path(Path.home(), '.config/mcm/').exists(): # pylint: disable=no-else-return
        return []
    else:
        with open(Path(Path.home(), '.config/mcm/saves.json'), 'r') as file:
            return json.loads(file.read())


def get_save_from_name(name):
    """
    return a save by name
    """
    return next((item for item in get_saves() if item['name'] == name), None)


def get_save_from_path(path):
    """
    return a save by path
    """
    return next((item for item in get_saves() if item['path'] == path), None)


def add_server(server_name, version_string, path):
    """
    add a server to the save list and save the file
    """
    server = dict()
    server['name'] = server_name
    server['version'] = version_string
    server['path'] = str(path)
    saves = get_saves()
    if get_save_from_name(server_name) or get_save_from_path(path):
        print('A server with that name or path already exists')
    saves.append(server)
    if not Path(Path.home(), '.config/mcm/').exists():
        Path(Path.home(), '.config/mcm/').mkdir(parents=True)
    with open(Path(Path.home(), '.config/mcm/saves.json'), 'wt') as file:
        file.write(json.dumps(saves, indent=4))
