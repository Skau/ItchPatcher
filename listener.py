import sys
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
            check_token()
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
        print(repository_name + " is not setup yet. Please enter the itch project name. (ex: user/game:platform)")
        project_name = input()
        config_parser[repository_name] = {'project': project_name}
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)
    print("Pushing via butler...")
    os.system("butler push " + "\"" + file_path + "\"" + " " + config_parser[repository_name]['project'])
    print("Butler push finished.")


def check_token():
    if not os.path.exists('config.ini'):
        f = open('config.ini', "w+")
        f.close()
        config_parser.read("config.ini")
        print("Config file not setup. Please enter you personal access token")
        token = input()
        config_parser['DEFAULT'] = {'token': token}
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)
        configfile.close()
    authorize()


def authorize():
    if github.authorize(config_parser=config_parser):
        print("Authorization successful! Authorized as " + github.user)
    else:
        print("Personal access token is not valid.")
        print("Please update config.ini with a legit personal access token.")


def readme():
    if os.path.exists('README.md'):
        file = open('README.md', 'r')
        for x in file:
            print(x)
        file.close()
    else:
        print("Could not find readme file.")


def stats():
    github.get_stats()
    pass


def itch_instant_upload():
    path = sys.argv[3]
    if not os.path.exists(path):
        print("Error: Path not found!")
        return
    repo = sys.argv[2]
    repos = github.get_repo_names()
    for item in enumerate(repos):
        if item[1] == repo:
            upload(path, repo)
            return
    print("Error: Could not find repo")


def main():
    length = len(sys.argv)
    if length == 1:
        check_token()
        app.run()
    else:
        arg1 = sys.argv[1]
        if arg1 == 'help':
            readme()
        else:
            check_token()
            if arg1 == 'stats':
                stats()
            elif arg1 == 'itch':
                itch_instant_upload()
            else:
                print("Argument(s) not supported. use 'listener.py help' for more info")


if __name__ == '__main__':
    main()
