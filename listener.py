import sys
import os
import shutil
from configparser import ConfigParser
from flask import Flask, request, abort
from itch import Itch
from github import GitHub


app = Flask(__name__)
itch = Itch()
config_parser = ConfigParser()
github = GitHub(config_parser)



@app.route('/', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.method == 'POST':
        data = request.json
        if data['action'] == 'published':
            print("Release event (published) received")
            release_data = github.download_file(data)
            name = release_data.repository_name
            config_parser.read('config.ini')

            if name not in config_parser:
                print(name + " is not setup yet. Please enter the itch project name. (ex: user/game:platform)")
                project_name = input()
                config_parser[name] = {'project': project_name}
                with open('config.ini', 'w') as configfile:
                    config_parser.write(configfile)

            print("Pushing via butler...")
            os.system("butler push " + "\"" + release_data.file_path + "\"" + " " + config_parser[name]['project'])

        current_directory = os.getcwd()
        downloads_path = os.path.join(current_directory, r'downloads')
        if os.path.exists(downloads_path):
            shutil.rmtree(downloads_path)
            print("Removed temp file")

        print("Done!")
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run()

