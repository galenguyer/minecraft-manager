"""
option parsing file for the minecraft manager
"""
import argparse


def main():
    """
    main method for parsing arguments
    """
    parser = argparse.ArgumentParser(prog='mcm', \
        description='minecraft server creator with start script and systemd service')
    parser.parse_args()


if __name__ == '__main__':
    main()
