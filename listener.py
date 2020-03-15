import sys
import argparse
import os
import shutil
from configparser import ConfigParser
from flask import Flask, request, abort
from github import GitHub

github = GitHub()
app = Flask(__name__)
config_parser = ConfigParser()


@app.route('/', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.method == 'POST':
        data = request.json
        if data['action'] == 'published':
            print("Release event (published) received")
            release_data = github.download_file(data)
            name = release_data.repository_name
            file_path = release_data.file_path
            upload(file_path, name)
            current_directory = os.getcwd()
            downloads_path = os.path.join(current_directory, r'downloads')
            if os.path.exists(downloads_path):
                shutil.rmtree(downloads_path)
                print("Removed temp file.")
                print("Done!")
        return '', 200
    else:
        abort(400)


def upload(file_path, repository_name):
    config_parser.read('config.ini')
    if repository_name not in config_parser:
        print(f'{repository_name} is not setup yet. Please enter the itch project name. (ex: user/game:platform)')
        project_name = input()
        config_parser[repository_name] = {'project': project_name}
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)
    print("Pushing via butler...")
    os.system(f"butler push \"{file_path}\" {config_parser[repository_name]['project']}")
    print("Butler push finished.")


def authorize():
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w+') as file:
            config_parser.read(file)
            print("Config file not setup. Please enter you personal access token:")
            token = input()
            config_parser['DEFAULT'] = {'token': token}
            config_parser.write(file)
            file.seek(0)
    config_parser.read('config.ini')
    token = config_parser['DEFAULT']['token']
    if github.authorize(token):
        print(f'Authorization successful! Authorized as {github.user}')
        return True
    else:
        print("Error: Personal access token is not usable.")
        print("Please update config.ini with a legit personal access token.")
        return False


def readme():
    try:
        with open('README.md') as file:
            print(file.read())
    except FileNotFoundError:
        print("Could not find readme file.")


def stats():
    github.get_stats()
    pass


def itch_instant_upload(repo, path):
    if not os.path.exists(path):
        print("Error: Path not found!")
        return
    repos = github.get_repo_names()
    for i, item in enumerate(repos):
        if item == repo:
            upload(path, repo)
            return
    print("Error: Could not find repo")


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

    authorize()
    any_parsed = False
    if args.readme:
        any_parsed = True
        readme()
    if args.stats:
        any_parsed = True
        stats()
    if args.itch:
        any_parsed = True
        itch_instant_upload(repo=args.repo, path=args.path)
    if args.run:
        any_parsed = True
        run()
    if not any_parsed:
        run()