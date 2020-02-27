import os
import requests
from collections import namedtuple

BASE_URL = "https://api.github.com"

ReleaseData = namedtuple("ReleaseData", "file_path repository_name")

class GitHub:
    def __init__(self, config_parser) -> ReleaseData:
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Itch Updater'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.session.headers.update({'Content-Type': 'application/json'})

        if not os.path.exists('config.ini'):
            f = open('config.ini', "w+")
            f.close()
            config_parser.read("config.ini")
            print("Config file not setup. Please enter you personal access token")
            token = input()
            config_parser['DEFAULT'] = {'token': token}
            with open('config.ini', 'w') as configfile:
                config_parser.write(configfile)

        token = config_parser['DEFAULT']['token']
        self.session.auth = ('access_token', token)
        r = self.session.get(url=BASE_URL + "/user")
        self.authorized = r.status_code == requests.codes.ok
        if self.authorized:
            json = r.json()
            print("Authorization successful! Authorized as " + json['login'])
        else:
            print("Please update config.ini with a legit personal access token.")

    def download_file(self, data):
        if not self.authorized:
            print("Personal access token is not valid. Could not process webhook")
            return

        assets = data['release']['assets']
        if len(assets) == 0:
            print("No asset was uploaded! No can do.")
            return

        asset = assets[0]
        asset_url = asset['url']
        asset_name = asset['name']
        self.session.headers.update({'Accept': 'application/octet-stream'})
        print("Downloading file..")
        r = self.session.get(asset_url)
        if r.status_code != requests.codes.ok:
            print("Could not retrieve file!")
            return

        current_directory = os.getcwd()
        downloads_path = os.path.join(current_directory, r'downloads')
        if not os.path.exists(downloads_path):
            os.mkdir(downloads_path)
        file_path = os.path.join(downloads_path, asset_name)
        file_binary = r.content
        binary_format = bytearray(file_binary)
        open(file_path, 'w+b').write(binary_format)
        print("Temporary file downloaded to " + file_path)
        data = ReleaseData(file_path, data['repository']['full_name'])
        return data



