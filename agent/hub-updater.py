import requests
import os
host = "http://YOUR_IP"
try:
    response = requests.get(host + ":5210/d_h")
    with open( os.sep.join(["agent","hub_dump"]) + os.sep + str(response.headers['content-disposition'])[21:],'wb')as file:
        file.write(response.content)
    requests.get(host + ":5211/quit")
except Exception as e:
    print(str(e))

file_path = "web_app.py"
#file_path = os.sep.join(["agent","hub_dump","web_app.py-20221106114033"])
file = {"file":open(file_path,'rb')}

response = requests.post(host + ":5210/u_h", files=file)
print(response.text)
