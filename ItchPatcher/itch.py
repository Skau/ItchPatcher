import os
from configparser import ConfigParser
from ItchPatcher import github
config_parser = ConfigParser()


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


def instant_upload(repo, path):
    if not os.path.exists(path):
        print("Error: Path not found!")
        return
    repos = github.get_repo_names()
    for i, item in enumerate(repos):
        if item == repo:
            upload(path, repo)
            return
    print("Error: Could not find repo")