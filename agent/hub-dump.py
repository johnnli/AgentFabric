import json
import requests
import os

response = requests.get("http://YOUR_IP:5210/d_h")

with open( os.sep.join(["agent","hub_dump"]) + os.sep + str(response.headers['content-disposition'])[21:],'wb')as file:
    file.write(response.content)