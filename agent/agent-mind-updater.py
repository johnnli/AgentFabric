import json
import requests
import os

MIND_updated = {}
with open(os.sep.join(["MIND.json"]),'r')as file:
    MIND_updated=json.load(file)

requests.post(MIND_updated["messager"]["url"] + "sender", json=MIND_updated)