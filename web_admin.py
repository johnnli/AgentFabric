import datetime

from flask import Flask, send_file
from flask import request

import subprocess
app = Flask(__name__)

@app .route('/d_h')
def dump_hub():
    return send_file('web_app.py',as_attachment=True, attachment_filename='web_app.py-'+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')))
@app .route('/u_h', methods=["POST"])
def update_hub():
    f = request.files['file']

    f.save("web_app.py")
    #start_web_app()

    return "ok"
@app .route('/hi')
def hi():
    return "hi"

def start_web_app():
    subprocess.Popen("python web_app.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return "ok"
if __name__ == '__main__':
    #start_web_app()
    app.run(debug=False, use_reloader=False,port=5210,host='0.0.0.0')