import datetime
import time
from flask import Flask, send_file
from flask import request
import json
import os

app = Flask(__name__)

global MIND
global METRICS

MIND = {}
METRICS = {}

@app .route('/sender', methods=["POST"])
def s():
    global MIND

    new_MIND = json.loads(request.data)
    
    n = str(new_MIND["self"]["name"])

    if MIND.get(n) is None:
        MIND[n] = new_MIND
        MIND[n]["last"] = str(time.time())
    else:
        if sorted(MIND[n].items()) != sorted(new_MIND.items()):
            MIND[n] = new_MIND
            MIND[n]["last"] = str(time.time())

    return "OK"
@app .route('/reader')
def r():
    global MIND
    n = request.args.get('n')
    if n == "":
        return MIND
    else:
        return MIND[n]
@app .route('/readerv')
def rv():
    global MIND
    n = request.args.get('n')

    if MIND.get(n) is None:
        MIND[n] = {"last":str(time.time())}

    return str(MIND[n]["last"])
@app .route('/sendmetrics', methods=["POST"])
def sm():
    global METRICS
    
    got_data = json.loads(request.data)
    n = str(got_data["self"]["name"])

    for key in got_data:
        if METRICS[n].get(key) is not None:
            if key != "self" and key != "keep":
                if got_data.get("keep") is not None:
                    keep = int(got_data["keep"])
                    if keep > 0:
                        METRICS[n][key] = METRICS[n][key][(keep-1)*-1:]
                METRICS[n][key].append({"datetime" : datetime.datetime.now() ,"value" : got_data[key]})
        else:
            if key != "self" and key != "keep":
                METRICS[n][key] = [{"datetime" : datetime.datetime.now() ,"value" : got_data[key]}]

    return "OK"
@app .route('/agents')
def a():
    global METRICS
    ret = {}
    for item in METRICS:
        ret[item] = {
            "name" : str(item),
            "last" : METRICS[item]["last"]
        }
    return ret
@app .route('/metrics')
def m():
    global METRICS
    n = request.args.get('n')

    if n == "":
        return METRICS
    else:
        if METRICS.get(n) is None:
            METRICS[n] = {}
            return METRICS[n]
        else:
            if request.args.get('q') is not None:
                ret = {}

                q = str(request.args.get('q'))
                if METRICS[n].get(q) is not None:
                    if request.args.get('count') is not None:
                        if request.args.get('v') is not None:
                            return str(METRICS[n][q][int(request.args.get('count'))][str(request.args.get('v'))])
                        else:
                            ret = METRICS[n][q][int(request.args.get('count'))]   
                    else:
                        ret = {q:METRICS[n][q]}
                else:
                    for key in METRICS[n]:
                        if str(key).find(q) == 0:
                            ret[key] = METRICS[n][key]
            else:
                ret = METRICS[n]
            if request.args.get("get_last_value") is not None:
                ret = ret[str(request.args.get("get_last_value"))]
                
            if request.args.get("get_array") is not None:
                ret = json.loads(str(ret).replace("'",'"'))
                return {"value": ret[int(request.args.get("get_array"))]} 
            elif request.args.get("get_dict") is not None:
                ret = json.loads(str(ret).replace("'",'"'))
                return {"value": ret[str(request.args.get("get_dict"))]}

            return ret
@app .route('/metricsc')
def mc():
    global METRICS
    n = request.args.get('n')
    if n == "":
        METRICS = {}
    else:
        METRICS[n] = {"last":0}

    return METRICS
@app .route('/metricsv')
def mv():
    global METRICS
    n = request.args.get('n')

    if METRICS.get(n) is None:
        METRICS[n] = {"last":str(time.time())}

    return str(METRICS[n]["last"])
@app .route('/heart')
def h():
    global METRICS
    n = request.args.get('n')
    METRICS[n]["last"] = str(time.time())

    return str(METRICS[n]["last"])
@app .route('/my_ip')
def m_i():
    return str(request.remote_addr)
@app .route('/f_s', methods=["POST"])
def file_send():
    f = request.files['file']

    f.save(os.path.join("files", f.filename))

    print(request.files, f.filename)

    return f.filename
@app .route('/f_d')
def file_download():
    n = request.args.get('n')
    f = request.args.get('f')

    global METRICS

    if METRICS[n] is not None:
        pass
    else:
        # sorry, no package(s) for you yet...
        pass

    return
@app.route('/quit')
def _quit():
    #os.system("python web_admin.py")
    #subprocess.Popen("python web_admin.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os._exit(0)

@app .route('/hi')
def hi():
    return "hi23"


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False,port=5211,host='0.0.0.0')