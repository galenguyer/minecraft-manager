"""
option parsing file for the minecraft manager
"""
import argparse
import os
import sys
import time
import json
from pathlib import Path
from urllib.request import urlopen, urlretrieve

from .utils import reporthook
from .scripts import create_start_script, create_systemd_file
from .saves import add_server, get_save_from_path, get_save_from_name


MEM_SIZE = min(((os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))/(1024.**3)), 4)


def get_path(args):
    """
    get the path to save files given the command line arguments
    """
    # if a path argument was given, use that first
    if args.path or args.name:
        if args.path:
            path = Path(args.path).resolve()
            print(f'prioritizing path argument, saving to {path}')
        elif args.name:
            path = Path(Path.cwd(), args.name)
            print(f'name given but no path, saving to {path}')
        # if the path exists, exit, otherwise create it
        if not path.exists():
            try:
                path.mkdir(parents=True)
            except: # pylint: disable=bare-except
                print(f'error creating path {path}, exiting')
                sys.exit(1)
        else:
            print(f'{path} already exists. not overwriting')
            sys.exit(1)
    else:
        path = Path.cwd()
        # ensure we have write permissions to the path
        if os.access(os.path.dirname(path), os.W_OK):
            print(f'using current directory {path}')
        else:
            print(f'no permissions to {path}, exiting')
            sys.exit(1)
    return path


def create_vanilla(args): # pylint: disable=too-many-branches,too-many-statements
    """
    repl loop for vanilla minecraft
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

    # if a name argument was provided, make sure it's valid
    if args.name:
        server_name = args.name.strip()
        for char in server_name:
            if not (char.isalpha() or char.isnumeric()):
                print(f'invalid character "{char}" in name. only letters and numbers are allowed')
                sys.exit(1)


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
    print(f'Using vanilla server version {selected_version}')

    path = get_path(args)

    # if no name was given, derive it from the base name of the directory
    if not args.name:
        server_name = path.name

    if get_save_from_name(server_name) or get_save_from_path(path):
        print('a server with that name or path already exists')
        sys.exit(1)

    urlretrieve(server_url, f'{path}/minecraft-server-{selected_version}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded minecraft-server-{selected_version}.jar to {path}')

    create_start_script(server_name, path, f'minecraft-server-{selected_version}.jar')
    create_systemd_file(server_name, path)
    add_server(server_name, f'{selected_version}', path)

    #print('If you opted to create a systemd service, start the server by running ' + \
    #    f'"systemctl start {server_name}" as root')
    print(f'Otherwise, run it with "java -jar -Xms{MEM_SIZE}G -Xmx{MEM_SIZE}G ' + \
        f'minecraft-server-{selected_version}.jar nogui". The -Xm options refer to ' + \
        'minimum and maximum memory allocated to the JVM. Only edit these if you ' + \
        'experience performance issues and you know what you\'re doing.')
    sys.exit(0)


def create_paper(args):
    """
    papermc download handler
    """
    # valid versions can have 4 structures
    # no version provided defaults to the latest build, as does 'latest'
    # a single string with no '-' will be treated as a simple version
    # the latest build of the specified version will be downloaded, if available
    # a string with a '-', such as '1.16.3-224' will be treated as a version and build
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
    print(f'using paper version {version}, build {build}')

    # if a name argument was provided, make sure it's valid
    if args.name:
        server_name = args.name.strip()
        for char in server_name:
            if not (char.isalpha() or char.isnumeric()):
                print(f'invalid character "{char}" in name. only letters and numbers are allowed')
                sys.exit(1)

    path = get_path(args)

    # if no name was given, derive it from the base name of the directory
    if not args.name:
        server_name = path.name

    if get_save_from_name(server_name) or get_save_from_path(path):
        print('a server with that name or path already exists')
        sys.exit(1)

    urlretrieve(f'https://papermc.io/api/v1/paper/{version}/{build}/download', \
        f'{path}/paper-{version}-{build}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded paper-{version}-{build}.jar to {path}')

    create_start_script(server_name, path, f'{path}/paper-{version}-{build}.jar')
    create_systemd_file(server_name, path)
    add_server(server_name, f'{version}-{build}', path)

    #print('If you opted to create a systemd service, start the server by running ' + \
    #    f'"systemctl start {server_name}" as root')
    print(f'Otherwise, run it with "java -jar -Xms{MEM_SIZE}G -Xmx{MEM_SIZE}G ' + \
        f'paper-{version}-{build}.jar nogui". The -Xm options refer to ' + \
        'minimum and maximum memory allocated to the JVM. Only edit these if you ' + \
        'experience performance issues and you know what you\'re doing.')
    sys.exit(0)

def handle_create(args):
    """
    dispatch creation of a server to the proper module
    """
    if args.module == 'vanilla' or args.module == 'minecraft':
        create_vanilla(args)
    elif args.module == 'paper':
        create_paper(args)



def main():
    """
    main method for parsing arguments
    """
    parser = argparse.ArgumentParser(prog='mcm')

    subparsers = parser.add_subparsers(title='available actions',
        metavar='action')

    create_parser = subparsers.add_parser(
        'create',
        help='create a new server with start script and systemd file'
    )

    create_parser.add_argument('module', help='the module to use when creating a server',
        choices=['vanilla', 'minecraft', 'paper'])
    create_parser.add_argument('--version', '-v', help='the version of the selected server to use')
    create_parser.add_argument('--path', '-p', help='path to save the jar to')
    create_parser.add_argument('--name', '-n',
        help='the name of the server, mostly used for the systemd file')
    create_parser.set_defaults(handle=handle_create)

    args = parser.parse_args()
    if hasattr(args, 'handle'):
        args.handle(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
