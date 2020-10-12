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
    if not Path(Path.home(), '.config/mcm/').exists() or \
        not Path(Path.home(), '.config/mcm/saves.json').exists(): # pylint: disable=no-else-return
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


def save_exists(name, path):
    """
    return whether or not a save exists
    """
    return get_save_from_name(name) or get_save_from_path(path)


def add_server(name, fork, version, path):
    """
    add a server to the save list and save the file
    """
    server = dict()
    server['name'] = name
    server['fork'] = fork
    server['version'] = version
    server['path'] = str(path)
    saves = get_saves()
    if save_exists(name, path):
        print('A server with that name or path already exists')
    saves.append(server)
    if not Path(Path.home(), '.config/mcm/').exists():
        Path(Path.home(), '.config/mcm/').mkdir(parents=True)
    with open(Path(Path.home(), '.config/mcm/saves.json'), 'wt') as file:
        file.write(json.dumps(saves, indent=4))


def update_server_version(name, version):
    """
    update a server's version
    """
    saves = get_saves()

    server = get_save_from_name(name)
    server['version'] = version

    for i, item in enumerate(saves):
        if item['name'] == name:
            saves[i] = server
            break

    if not Path(Path.home(), '.config/mcm/').exists():
        Path(Path.home(), '.config/mcm/').mkdir(parents=True)
    with open(Path(Path.home(), '.config/mcm/saves.json'), 'wt') as file:
        file.write(json.dumps(saves, indent=4))
