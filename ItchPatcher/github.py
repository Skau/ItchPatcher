import os
import requests
from collections import namedtuple
from configparser import ConfigParser

config_parser = ConfigParser()

BASE_URL = "https://api.github.com"

ReleaseData = namedtuple("ReleaseData", "file_path repository_name")


class GitHub:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Itch Updater'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.user = ""
        self.authorized = self.authorize()

    def authorize(self,):
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
        self.session.auth = ('access_token', token)
        r = self.session.get(url="{}/user".format(BASE_URL))
        self.authorized = r.status_code == requests.codes.ok
        if self.authorized:
            json = r.json()
            self.user = json['login']
            print(f'Authorization successful! Authorized as {self.user}')
            return True
        else:
            print("Error: Personal access token is not usable.")
            print("Please update config.ini with a legit personal access token.")
            return False

    def download_file(self, data):
        if not self.authorized:
            print("Error: Personal access token is not usable.")
            print("Please update config.ini with a legit personal access token.")
            return

        assets = data['release']['assets']
        if len(assets) == 0:
            print("Error: No asset was uploaded with this release.")
            return

        asset = assets[0]
        asset_url = asset['url']
        asset_name = asset['name']
        self.session.headers.update({'Accept': 'application/octet-stream'})
        print("Downloading file..")
        r = self.session.get(asset_url)
        if r.status_code != requests.codes.ok:
            print("Error: Could not retrieve file!")
            return

        current_directory = os.getcwd()
        downloads_path = os.path.join(current_directory, r'downloads')
        if not os.path.exists(downloads_path):
            os.mkdir(downloads_path)
        file_path = os.path.join(downloads_path, asset_name)
        file_binary = r.content
        binary_format = bytearray(file_binary)
        open(file_path, 'w+b').write(binary_format)
        print(f'Temporary file downloaded to {file_path}')
        data = ReleaseData(file_path, data['repository']['full_name'])
        return data

    def get_stats(self):
        if not self.authorized:
            print("Error: Personal access token is not usable.")
            print("Please update config.ini with a legit personal access token.")
            return

        additions = 0
        deletions = 0
        commits = 0
        print(f'Getting total number of commits, code additions and deletions for {self.user}..')
        repos = self.get_repos()
        total_repos = len(repos)
        print(f'Found {total_repos} repos.')
        print_progress_bar(0, total_repos)
        for i, item in enumerate(repos):
            r = self.session.get(url=f"{BASE_URL}/repos/{item['full_name']}/stats/contributors")
            if r.status_code is not requests.codes.ok:
                continue
            stats = r.json()[0]
            for stat in stats['weeks']:
                additions += int(stat['a'])
                deletions += int(stat['d'])
                commits += int(stat['c'])
            print_progress_bar(i + 1, total_repos)

        print("Finished")
        print(f'Total number of commits: {commits}')
        print(f'Total number of code additions: {additions}')
        print(f'Total number of code deletions: {deletions}')
        print("""
        NOTE: These stats might not be completely accurate.
        GitHub will only track contributions when the following is met:
        - The email address used for the commits is associated with this GitHub account.
        - Commits are in the repo's default branch (usually master) or gh-pages for repos with project sites.
        - At least one of the following must be true: 
          User is a collaborator, forked the repo, opened a pull request or issue, starred the repository.
        - If it is a fork, it will not count unless the commits are added as a pull request in the parent
          repository, or detaching the fork and turning it into its own standalone repository.
        Also note that GitHub cache contributions to save bandwidth.
        You should run this one more time just in case some data has not been fetched in a while
        for a potentially more accurate result.
        """)

    def get_repos(self):
        if self.authorized:
            ret = []
            r = self.session.get(url=f'{BASE_URL}/user/repos')
            link = str(r.headers['link'])
            first = link[link.find('next'):]
            result = first[first.find('page'):]
            total_pages = int(result[5])
            current_page = 1
            while current_page < total_pages:
                r = self.session.get(url=f'{BASE_URL}/user/repos?per_page=100&page={current_page}')
                if r.status_code is not requests.codes.ok:
                    continue
                ret += r.json()
                current_page += 1
            return ret

    def get_repo_names(self):
        repos = self.get_repos()
        ret = []
        for repo in repos:
            ret.append(repo['full_name'])
        return ret


def print_progress_bar(iteration, total):
    percent = ("{0:." + str(1) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(50 * iteration // total)
    bar = '█' * filled_length + '-' * (50 - filled_length)
    print(f'Progress: |{bar}| {percent}% Complete', end="\r")
    if iteration == total:
        print()

