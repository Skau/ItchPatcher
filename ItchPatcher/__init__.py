from flask import Flask
from ItchPatcher.github import GitHub


github = GitHub()
app = Flask('ItchPatcher')

