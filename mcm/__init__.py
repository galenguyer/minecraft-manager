"""
option parsing file for the minecraft manager
"""
import argparse

from .create import create_vanilla, create_paper


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
