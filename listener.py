import sys

from flask import Flask, request, abort
from patcher import ItchPatcher
from github import GitHub

app = Flask(__name__)
itch_patcher = ItchPatcher()
github = GitHub()


@app.route('/', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.method == 'POST':
        data = request.json
        if data['action'] == 'published':
            print("Release event (published) received")
            file_path = github.download_file(data)
            itch_patcher.upload(file_path)
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run()

