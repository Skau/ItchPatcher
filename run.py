import argparse
import sys
from ItchPatcher import app, github
from ItchPatcher.itch import instant_upload


def stats():
    github.get_stats()
    pass


def readme():
    try:
        with open('README.md') as file:
            print(file.read())
    except FileNotFoundError:
        print("Could not find readme file.")


def run():
    app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ItchPatcher', description="Utility functions for git and itch.")
    parser.add_argument('-run', action='store_true', help="Starts listening. "
                                                          "Can also be started by not passing any arguments")
    parser.add_argument('-readme', action='store_true', help="Prints README.md")
    parser.add_argument('-stats', action='store_true', help="Iterates through all repos the user is a "
                                                            "part of and prints commits, code additions and deletions")
    parser.add_argument('-itch', action='store_true',
                        help="Instantly uploads the specified filepath to the itch project "
                             "associated in config.ini by the specified repo. Requires -repo and -path")
    parser.add_argument('-repo', required='-itch' in sys.argv, help="The repository")
    parser.add_argument('-path', required='-itch' in sys.argv, help="The filepath")
    args = parser.parse_args()

    any_parsed = False
    if args.readme:
        any_parsed = True
        readme()
    if args.stats:
        any_parsed = True
        stats()
    if args.itch:
        any_parsed = True
        instant_upload(repo=args.repo, path=args.path)
    if args.run:
        any_parsed = True
        run()
    if not any_parsed:
        run()
