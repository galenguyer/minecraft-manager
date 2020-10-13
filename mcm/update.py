"""
methods to update a server to a given version
"""
import sys
import time
import json
from urllib.request import urlopen, urlretrieve

import requests
from bs4 import BeautifulSoup

from .utils import reporthook
from .scripts import create_start_script
from .saves import update_server_version, get_save_from_name


def update_paper(args, save):
    """
    update a given paper server
    """
    paper_versions = json.loads(
        urlopen('https://papermc.io/api/v1/paper')\
            .read().decode('utf-8'))
    if args.version is None or args.version == 'latest':
        version = paper_versions['versions'][0]
    else:
        version = args.version.partition('-')[0]
        if version not in paper_versions['versions']:
            print(f'invalid paper version {args.version}')
            sys.exit(1)
    # now that we have a good version, get the build number
    paper_builds = json.loads(
        urlopen(f'https://papermc.io/api/v1/paper/{version}')\
            .read().decode('utf-8'))
    if args.version is not None and '-' in args.version:
        build = args.version.partition('-')[2]
        if build not in paper_builds['builds']['all']:
            print(f'invalid paper build {build}')
            sys.exit(1)
    else:
        build = paper_builds['builds']['latest']
    print(f'updating to paper version {version}, build {build}')

    urlretrieve(f'https://papermc.io/api/v1/paper/{version}/{build}/download', \
        f'{save["path"]}/paper-{version}-{build}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded paper-{version}-{build}.jar to {save["path"]}')

    create_start_script(save['name'], save['path'], f'{save["path"]}/paper-{version}-{build}.jar')
    update_server_version(save['name'], f'{version}-{build}')

    print(f'{save["name"]} updated to version paper-{version}-{build}. ' + \
        'if you\'re using systemd, be sure to restart the server')


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
    update_server_version(save['name'], f'{selected_version}')

    print(f'{save["name"]} updated to version {selected_version}. ' + \
        'if you\'re using systemd, be sure to restart the server')


def update_forge(args, save): # pylint: disable=too-many-branches
    """
    forge download handler
    """
    if args.version is None or args.version == 'latest':
        page = requests.get('https://files.minecraftforge.net/')
    else:
        version = args.version.partition('-')[0]
        page = requests.get(f'https://files.minecraftforge.net/maven/net/minecraftforge/forge/index_{version}.html')
    if page.status_code  != 200:
        print(f'invalid forge version {version}')
        sys.exit(1)

    parsed_page = BeautifulSoup(page.text, 'html.parser')
    if args.version is not None and '-' in args.version:
        links = [e['href'] for e in parsed_page.find_all('a') if \
            'Direct Download' in e.text and 'universal' in e['href'] \
            and f'/{args.version}' in e['href']]
        if len(links) > 0:
            link = links[0]
        else:
            print(f'invalid build {args.version}')
            sys.exit(1)
    
    link = parsed_page.find_all('div', attrs={'class': 'download'})[0].find_all('div', attrs={'class': 'link'})[-1].find_all('a')[0]['href'].partition('url=')[2] if args.version == 'latest' or len(parsed_page.find_all('div', attrs={'class': 'download'})) == 1 else parsed_page.find_all('div', attrs={'class': 'download'})[1].find_all('div', attrs={'class': 'link'})[-1].find_all('a')[0]['href'].partition('url=')[2]

    version = link.partition('/forge/')[2].partition('/')[0].partition('-')[0] + '-' + link.partition('/forge/')[2].partition('-')[2].partition('-')[0].partition('/')[0]
    print(f'updating to forge version {version}')

    path = save['path']

    urlretrieve(link, f'{path}/forge-{version}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded forge-{version}.jar to {path}')

    create_start_script(save['name'], path, f'{path}/forge-{version}.jar')
    update_server_version(save['name'], f'{version}')

    print(f'{save["name"]} updated to version {version}. ' + \
    'if you\'re using systemd, be sure to restart the server')


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
    elif save['fork'] == 'forge':
        update_forge(args, save)
    else:
        print(f'uh oh, someone made a fucky wucky, there\'s no updater for the {save["fork"]} fork yet')
