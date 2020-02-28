import sys
import os
import shutil
from configparser import ConfigParser
from flask import Flask, request, abort
from github import GitHub


app = Flask(__name__)
config_parser = ConfigParser()


@app.route('/', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.method == 'POST':
        data = request.json
        if data['action'] == 'published':
            print("Release event (published) received")
            authorize()
            github = GitHub(config_parser)
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


def authorize():
    if not os.path.exists('config.ini'):
        f = open('config.ini', "w+")
        f.close()
        config_parser.read("config.ini")
        print("Config file not setup. Please enter you personal access token")
        token = input()
        config_parser['DEFAULT'] = {'token': token}
        with open('config.ini', 'w') as configfile:
            config_parser.write(configfile)


def main():
    length = len(sys.argv)
    if length > 1:
        if length == 2 and sys.argv[1] == 'help' and os.path.exists('README.md'):
            file = open('README.md', 'r')
            for x in file:
                print(x)
            file.close()
        elif length == 3:
            repo = sys.argv[1]
            authorize()
            if os.path.exists(sys.argv[2]):
                upload(sys.argv[2], repo)
    else:
        authorize()
        app.run()


if __name__ == '__main__':
    main()
