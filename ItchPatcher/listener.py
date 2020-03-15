import sys
import os
import shutil
from configparser import ConfigParser
from flask import request, abort
from ItchPatcher import app, github
from ItchPatcher.itch import upload
config_parser = ConfigParser()


@app.route('/', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.method == 'POST':
        data = request.json
        if data['action'] == 'published':
            github.authorize()
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
