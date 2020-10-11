"""
common utils
"""
import os
import sys
import time


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
