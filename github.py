import os
import requests

BASE_URL = "https://api.github.com"


class GitHub:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Itch Updater'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.session.headers.update({'Content-Type': 'application/json'})
        file = open("token.txt")
        token = file.readline()
        file.close()
        self.session.auth = ('access_token', token)
        r = self.session.get(url=BASE_URL + "/user")
        self.authorized = r.status_code == requests.codes.ok
        if self.authorized:
            json = r.json()
            print("Authorization successful! Authorized as " + json['login'])
        else:
            print("Please provide a legit personal access token")

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
            return;

        current_directory = os.getcwd()
        downloads_path = os.path.join(current_directory, r'downloads')
        if not os.path.exists(downloads_path):
            os.mkdir(downloads_path)
        file_path = os.path.join(downloads_path, asset_name)
        file_binary = r.content
        binary_format = bytearray(file_binary)
        open(file_path, 'w+b').write(binary_format)
        print("Temporary file downloaded to " + file_path)
        return file_path



