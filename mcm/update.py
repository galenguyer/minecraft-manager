"""
methods to update a server to a given version
"""
import sys

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
    _, _ = args, save


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
