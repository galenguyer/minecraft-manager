"""
methods to update a server to a given version
"""
import sys
import time
import json
from urllib.request import urlopen, urlretrieve

from .utils import reporthook
from .scripts import create_start_script
from .saves import get_save_from_name


def update_paper(args, save):
    """
    update a given paper server
    """
    _, _ = args, save


def update_vanilla(args, save):
    """
    update a given vanilla server
    """
    # load list of all versions from mojang's metadata
    versions = json.loads(
        urlopen('https://launchermeta.mojang.com/mc/game/version_manifest.json')\
            .read().decode('utf-8'))

    # get the latest version of minecraft if none was provide
    if args.version is None or args.version.lower() == 'latest':
        selected_version = versions['latest']['release']
    else:
        selected_version = args.version.lower()

    # get the download url for the server jar or exit if the version is not found
    server_url = None
    for version in versions['versions']:
        if version['id'] == selected_version:
            version_json = json.loads(urlopen(version['url']).read().decode('utf-8'))
            server_url = version_json['downloads']['server']['url']
            break
    if server_url is None:
        print(f'Invalid version {selected_version}. Exiting')
        sys.exit(1)
    print(f'updating to vanilla server version {selected_version}')

    urlretrieve(server_url, f'{save["path"]}/minecraft-server-{selected_version}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded minecraft-server-{selected_version}.jar to {save["path"]}')

    create_start_script(save['name'], save['path'], f'minecraft-server-{selected_version}.jar')

    print(f'{save["name"]} updated to version {selected_version}. ' + \
        'if you\' using systemd, be sure to restart the server')


def update_server(args):
    """
    receive args and dispatch to fork as needed
    """
    save = get_save_from_name(args.name)
    if save is None:
        print(f'could not find save with name {args.name}')
        sys.exit(1)
    if save['fork'] == 'paper':
        update_paper(args, save)
    elif save['fork'] == 'vanilla':
        update_vanilla(args, save)
