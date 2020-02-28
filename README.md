# ItchPatcher

Updates itch projects automatically when new GitHub releases are made!

The program will listen to release event webhooks from GiHub. 
This all happens locally!

## Requirements
- Python3
- butler, which is a itch.io command line tool found [here](https://itch.io/docs/butler/installing.html).
- ngrok or a similair tunneling service to route the webhook to your localhost

## Setup
To enable webhooks you need to add the webhook in the repositores you want ItchPatcher to listen to release events on.
This can be done in your repository -> Settings -> Webhooks -> Add webhook.

The webhook to add would be your routing to your localhost.
Example using ngrok:
- Download ngrok from [here](https://ngrok.com/download).
- cd to the location you put the .exe file
- run *ngrok http 5000* (5000 means the port, and you can choose whatever, doesn't matter).
- Then the session status will pop up, the forwading url which looks something like *https://xxxxx.ngrok.io* is the one to use as webhook.
- When adding the webook on GitHub, make sure to check *Let me select individual events* and then *Releases*.

When the webhook is setup you can download or clone this project.
Then run *pip install -r requirements.txt* to install required packages.
Finally run listener.py

The first time running, the ItchPatcher will ask for your personal access token. 
This is so it will be possible to access your private repositories.
To create one go [here](https://github.com/settings/tokens/new).
Check 'repo' and hit genereate, then paste it into the command line and hit enter.
This will be cached in a config.ini file, change it here if you need to update it etc.

The config.ini file also holds the names of all your repositories and their associated itch project name.
When ItchPatcher sees a repository it hasn't cached in config.ini, it will prompt you for the project name and channel on itch.io,
ex (user/game:channel).
All of these will be cached in the config file, so you only have to enter them once. You can also directly edit the config file yourself if
you don't want to be prompted by ItchPatcher.

Note: Currenly only supports compressed files, so remember to zip your packaged game before uploading them to the release.
This is what butler recommends anyways for faster uploads.

## Other commands

- *$ listener.py help* - will print this readme.
- *$ listener.py repo filepath* - will use the itch project associated with the repo (or prompt you to add it) in config.ini and patch the project with the specified file directly. This allows you to use the service without the webhook part, just as a shortcut instead of using butler directly.
