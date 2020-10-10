"""
option parsing file for the minecraft manager
"""
import os
import sys
import time
import json
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


def minecraft():
    """
    repl loop for vanilla minecraft
    """
    versions = json.loads(
        urlopen('https://launchermeta.mojang.com/mc/game/version_manifest.json')\
            .read().decode('utf-8'))
    uver = input('What version of Minecraft would you like? ' + \
        f'The default is the lateset release ({versions["latest"]["release"]}): ')
    if uver:
        uver = uver.lower()
    else:
        uver = versions['latest']['release']

    server_url = None
    for version in versions['versions']:
        if version['id'] == uver:
            version_json = json.loads(urlopen(version['url']).read().decode('utf-8'))
            server_url = version_json['downloads']['server']['url']
            break
    if server_url is None:
        print(f'Invalid version {uver}. Exiting')
        sys.exit(1)

    path = input('Where would you like file saved? ' + \
        f'The default is the current directory ({os.getcwd()})')
    if not path:
        path = os.getcwd()
    if path[-1] != '/':
        path += '/'
    if os.path.exists(path) or os.access(os.path.dirname(path), os.W_OK):
        urlretrieve(server_url, f'{path}minecraft-server-{uver}.jar', reporthook)
        time.sleep(0.5)
        print(f'\nDownloaded minecraft-server-{uver}.jar to {path}')
    else:
        sys.exit(f'"{path}" is not a valid or writeable path')

    server_name = path.strip('/').split('/')[-1]
    print('\nDone!')
    print('If you opted to create a systemd service, start the server by running' + \
        f'"systemctl start {server_name}" as root')
    print(f'Otherwise, run it with "java -jar -Xms{MEM_SIZE}G -Xmx{MEM_SIZE}G ' + \
        f'minecraft-server-{uver}.jar nogui". The -Xm options refer to' + \
        'minimum and maximum memory allocated to the JVM. Only edit these if you' + \
        'experience performance issues and you know what you\'re doing.')
    sys.exit(0)

def main():
    """
    main method for parsing arguments
    """
    if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        print('Pure REPL script to create a minecraft server ' + \
            'with a start script and optional systemd file')
        sys.exit(0)
    module = input('Select a module to use or type "list" to see available modules: ')
    if not module or module == 'list':
        print('Available modules: minecraft')
        sys.exit(0)
    if module == 'minecraft':
        minecraft()
    else:
        print('No valid module selected')
        sys.exit(1)

if __name__ == '__main__':
    main()
