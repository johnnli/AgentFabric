import json
import requests
import os

response = requests.get("http://YOUR_IP:5211/reader?n=Agent_Name")

MIND = json.loads(response.content)

with open(os.sep.join(["agent","MIND.json"]),'w')as file:
    file.write(response.text)