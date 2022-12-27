import json
import requests
import os

MIND_updated = ""
with open(os.sep.join(["agent","MIND.json"]),'r')as file:
    for line in file.readlines():
        MIND_updated += line

requests.post("http://YOUR_IP:5211/sender", data=MIND_updated)