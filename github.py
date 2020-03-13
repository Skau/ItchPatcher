import os
import time

import requests
from collections import namedtuple

BASE_URL = "https://api.github.com"

ReleaseData = namedtuple("ReleaseData", "file_path repository_name")


class GitHub:
    def __init__(self):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Itch Updater'})
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.authorized = False
        self.user = ""

    def authorize(self, config_parser):
        config_parser.read("config.ini")
        token = config_parser['DEFAULT']['token']
        self.session.auth = ('access_token', token)
        r = self.session.get(url=BASE_URL + "/user")
        self.authorized = r.status_code == requests.codes.ok
        if self.authorized:
            json = r.json()
            self.user = json['login']
            return True
        else:
            return False

    def download_file(self, data):
        if not self.authorized:
            print("Personal access token is not valid.")
            print("Please update config.ini with a legit personal access token.")
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

    def get_stats(self):
        if self.authorized:
            additions = 0
            deletions = 0
            commits = 0
            print("Getting total number of commits, code additions and deletions for " + self.user + "..")
            repos = self.get_repos()
            total_repos = len(repos)
            self.print_progress_bar(0, total_repos, prefix='Progress:', suffix='Complete', length=50)
            for i, item in enumerate(repos):
                r = self.session.get(url=BASE_URL + "/repos/" + item['full_name'] + "/stats/contributors")
                if r.status_code is not requests.codes.ok:
                    print("No data found")
                    continue
                stats = r.json()[0]
                for stat in stats['weeks']:
                    additions += int(stat['a'])
                    deletions += int(stat['d'])
                    commits += int(stat['c'])
                time.sleep(0.1)
                self.print_progress_bar(i + 1, total_repos, prefix='Progress:', suffix='Complete', length=50)
            print("Finished")
            print("Total number of commits: " + str(commits))
            print("Total number of code additions: " + str(additions))
            print("Total number of code deletions: " + str(deletions))
            print("NOTE: These stats might not be completely accurate.")
            print("GitHub will only track contributions when the following is met:")
            print("- The email address used for the commits is associated with this GitHub account.")
            print("- Commits are in the repo's default branch (usually master) or "
                  "gh-pages for repos with project sites.")
            print("- At least one of the following must be true: "
                  "User is a collaborator, forked the repo, opened a pull request or issue, starred the repository.")
            print("- If it is a fork, it will not count unless the commits are added as a pull request in the parent"
                  " repository, or detaching the fork and turning it into its own standalone repository.")
            print("Also note that GitHub cache contributions to save bandwidth. "
                  "You should run this one more time just in case some data has not been fetched in a while"
                  " for a potentially more accurate result.")
        else:
            print("Personal access token is not valid.")
            print("Please update config.ini with a legit personal access token.")

    def get_repos(self):
        if self.authorized:
            ret = []
            r = self.session.get(url=BASE_URL + "/user/repos")
            link = str(r.headers['link'])
            first = link[link.find('next'):]
            result = first[first.find('page'):]
            total_pages = int(result[5])
            current_page = 1
            done = 0
            while current_page < total_pages:
                r = self.session.get(url=BASE_URL + "/user/repos?per_page=100&page=" + str(current_page))
                if r.status_code is not requests.codes.ok:
                    print("Page not found")
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

    def print_progress_bar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=print_end)
        # Print New Line on Complete
        if iteration == total:
            print()
