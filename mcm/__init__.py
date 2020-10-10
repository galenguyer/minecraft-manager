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


MEM_SIZE = min(((os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'))/(1024.**3)), 4)


def reporthook(count, block_size, total_size):
    """
    used for printing the status of a download
    """
    global START_TIME # pylint: disable=global-variable-undefined
    if count == 0:
        START_TIME = time.time()
        return
    duration = time.time() - START_TIME
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write('\r%d%%, %d MB, %d KB/s, %d seconds passed' %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()


def get_is_root() -> bool:
    """
    return whether or not the script is being run as root
    """
    return os.getuid() == 0


def check_root() -> None:
    """
    ensure the user intends to run as not root if that's the case
    """
    if get_is_root():
        pass
    else:
        print('You are not running this script as root. ' + \
            'This means dependencies cannot be automatically installed, ' + \
            'and a service file cannot be created.')
        carryon = input('Are you sure you wish to continue? [yN]: ')
        if carryon.lower() == 'y':
            pass
        else:
            sys.exit('Please run the script as root to continue')


def create_start_script(server_name, path, jar_name):
    """
    create the startup script given a few arguments
    """
    start_script = f'''#!/usr/bin/env bash
## {server_name}.sh

# exit if a command fails
set -o errexit

# exit if required variables aren't set
set -o nounset

# return the exit status of the final command before a failure
set -o pipefail

# create a new named screen session for the server, killing any existing ones
if screen -list | grep -q "^{server_name}$"; then
    screen -S "{server_name}" -X quit 2>&1 >/dev/null
fi
screen -dmS "{server_name}" java -jar {jar_name} nogui
'''
    with open(Path(path, 'start.sh'), 'wt') as script_fd:
        script_fd.write(start_script)


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

    # if no name was given, derive it from the base name of the directory
    if not args.name:
        server_name = path.name

    urlretrieve(server_url, f'{path}/minecraft-server-{selected_version}.jar', reporthook)
    time.sleep(0.5)
    print(f'\nDownloaded minecraft-server-{selected_version}.jar to {path}')

    create_start_script(server_name, path, f'minecraft-server-{selected_version}.jar')

    #print('If you opted to create a systemd service, start the server by running ' + \
    #    f'"systemctl start {server_name}" as root')
    print(f'Otherwise, run it with "java -jar -Xms{MEM_SIZE}G -Xmx{MEM_SIZE}G ' + \
        f'minecraft-server-{selected_version}.jar nogui". The -Xm options refer to ' + \
        'minimum and maximum memory allocated to the JVM. Only edit these if you ' + \
        'experience performance issues and you know what you\'re doing.')
    sys.exit(0)



def handle_create(args):
    """
    dispatch creation of a server to the proper module
    """
    if args.module == 'vanilla' or args.module == 'minecraft':
        create_vanilla(args)


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
        choices=['vanilla', 'minecraft'])
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
