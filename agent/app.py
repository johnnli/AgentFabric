#import numpy
from genericpath import isdir
from glob import glob
import json
import socket
import requests
import time
import os
import subprocess
import ast
# import pandas as pd
# from pyhive import hive

global MIND
global METRICS
MIND = {}
METRICS = {}

class common_method():
    def select(self, param):
        def get_from_md(filepath, filename):
            find_target = ["#Agent_Data"]
            find_tail = [""]

            with open(filepath,'r',encoding='utf-8')as file:
                for line in file.readlines():
                    for item_f_t in find_target:
                        for item_t in find_tail:
                            if line.find(item_f_t+item_t) > -1:
                                return str(filepath)
            return ""
        filelist=[]

        for file_item in os.listdir(param["folder"]):
            adding = get_from_md(os.sep.join([param["folder"], file_item]), file_item)
            if adding != "":
                filelist.append(adding)

        return filelist
    def get_from_web(self, param):
        global MIND
        params = ""
        if param.get("get_param") is not None:
            for item in param["get_param"]:
                if params == "":
                    params = "?" + str(item) + "=" +  get_from_context(str(param["get_param"][item]), MIND)
                else:
                    params += "&" + str(item) + "=" + get_from_context(str(param["get_param"][item]), MIND)
        
        if param.get("metrics_address") is not None:
            response = requests.get(param["metrics_address"]["url"] + params)
            return json.loads(response.content) 
        
        return {}
    # def select_pyhive(self, param):
    #     return {"database_name":{"1":1,"2":2,"3":3}}
    # def select_pyhive(self, param):
    #     conn = hive.connect(host=param["server"]["host"],port=param["server"]["port"],database=param["dbname"])
    #     cur = conn.cursor()
    #     try:
    #         df = pd.read_sql(param["hql"], conn)
    #         return df
    #     finally:
    #         if conn:
    #             conn.close()
    #     return 0
    def request_post(self, param):
        url = None
        data = None
        json = None
        kwargs = None

        if param.get("url") is not None:
            url = param["url"]
        if param.get("data") is not None:
            data = param["data"]
        if param.get("json") is not None:
            json = param["json"]
        if param.get("kwargs") is not None:
            kwargs = param["kwargs"]

        if url is not None:
            if kwargs is not None:
                response = requests.post(url, data=data, json=json, **kwargs)
            else:
                response = requests.post(url, data=data, json=json)
            return response.text

        return {}
    def request_get(self, param):
        if param.get("args") is not None:
            response = requests.get(**param["args"])
            return response.text

        return {}
    def excute_py(self, param):
        cmd_order = param["cmd"]
        cmd_param = []
        cmd_result = ""

        if param.get("param") is not None:
            params = ast.literal_eval(param["param"]["value"])
            if type(params).__name__=="list":
                cmd_param = params

        cmd = cmd_order

        if cmd_param != []:
            for item in cmd_param:
                cmd = cmd_order + " ['" + str(item).replace("\\","\\\\") + "']"
                cmd_p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for i in cmd_p.stdout.readlines():
                    cmd_result += i.decode();
                if cmd_result != "":
                    cmd_result += " ; "
        else:
            cmd_p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
            for i in cmd_p.stdout.readlines():
                cmd_result += i.decode();
        return {"excute_result":cmd_result.replace("\r\n","")}

    def json_count(self, param):
        ret = 0

        target = {}
        if type(param["input_json"]).__name__ == "str":
            target = json.loads(param["input_json"])
        else:
            target = param["input_json"]

        if target.get(param["count_name"]) is not None:
            ret = len(target[param["count_name"]])

        return ret
    
    def json_convert_from_str(self, param):
        target = str(param["target"]).replace("'",'"')
        return json.loads(target)
        input_a = param["input_a"]
        target= param["output"]

        if type(input_a[target]).__name__=="list" and param.get("count") is not None:
            return input_a[target][param["count"]]

        return input_a[target]
    
    def get_home_dir(self, param):
        return os.getcwd()
    def get_dir_files(self, param):
        ret = []
        if os.path.exists(param["path"]["value"]):
            for f in os.listdir(param["path"]["value"]):
                if os.path.isfile(os.sep.join([param["path"]["value"],f])):
                    ret.append(f)
        return ret
    def get_dir_folders(self, param):
        ret = []
        if os.path.exists(param["path"]["value"]):
            for f in os.listdir(param["path"]["value"]):
                if os.path.isdir(os.sep.join([param["path"]["value"],f])):
                    ret.append(f)
        return ret
    def get_parent_folder(self, param):
        ret = ""
        if os.path.exists(param["path"]["value"]):
            ret = os.path.abspath(os.path.dirname(param["path"]["value"]))
        return ret
    def get_join_path(self, param):
        ret = ""
        if os.path.exists(os.sep.join([param["path_a"]["value"],param["path_b"]["value"]]) ):
            ret = os.path.abspath(os.sep.join([param["path_a"]["value"],param["path_b"]["value"]]))
        return ret
    def get_ip(self, param):
        innner_ip = socket.gethostbyname(socket.gethostname())

        def getOutterIP(url):
            ip = ''    
            try:
                ip = requests.get(url, timeout=5).text
            except:
                pass
            return ip
        outter_ip = getOutterIP(param["outter_ip_getter_address"]['url'])

        return {"inner_ip":str(innner_ip), "outter_ip": str(outter_ip)}
    def exe_file(self, param):
        if param.get("app") is not None:
            if param.get("param") is not None:
                os.system(str(param["app"]["value"]) + " " + str(param["param"]["value"]))
            else:
                os.system(str(param["app"]["value"]))
        return
def upate_mind():
    global MIND
    print(time.strftime("%c") + ": " + requests.post(MIND["messager"]["url"] + "sender", data=json.dumps(MIND)))
    return
def refresh_mind():
    global MIND

    response = requests.get(MIND["messager"]["url"] + "reader?" + MIND["self"]["name"])
    MIND = json.loads(response.content)

    print(time.strftime("%c") + " " + MIND["self"]["name"] + " : MIND updated.")

    return
def chk_sleep_enough(last, sleep):
    return time.time() >= float(last)+float(sleep)
def chk_owns(own_obj, MIND, path, METRICS):
    for item_obj in own_obj:
        path_prefix = ""

        if path == "":
            path_prefix = item_obj["name"]
        else:
            path_prefix = path + "." + item_obj["name"]

        if item_obj.get("metrics") is not None:
            keepCount=0
            if item_obj.get("keep") is not None:
                keepCount = int(item_obj["keep"])
                
            for item_metrics in item_obj["metrics"]:
                if item_metrics.get("sleep") is not None:
                    if not chk_sleep_enough(METRICS["last"],item_metrics["sleep"]):
                        continue
                    METRICS["last"] = time.time()

                if item_metrics.get("query") is not None:
                    write_metrics(path_prefix + "." + item_metrics["name"], str(cal_metrics(item_metrics["query"], MIND)), MIND["messager"]["url"], METRICS,MIND["self"]["name"], keepCount)

        if item_obj.get("views") is not None:
            for item_metrics in item_obj["views"]:
                if item_metrics.get("sleep") is not None:
                    if not chk_sleep_enough(METRICS["last"],item_metrics["sleep"]):
                        continue
                    METRICS["last"] = time.time()

                if item_metrics.get("query") is not None:
                    print("Views got: " + item_metrics["name"] + " result:" + str(cal_metrics(item_metrics["query"], MIND)))

        if item_obj.get("owns") is not None:
            chk_owns(item_obj["owns"], MIND, path_prefix, METRICS)
    return
def write_metrics(name, value, url, METRICS, self_name, keepCount):
    changed = False

    if METRICS.get(name) is not None:
        if METRICS[name] != value and str(value).strip() != "":
            METRICS[name] = value
            changed = True
    else:
        if str(value).strip() != "":
            METRICS[name] = value
            changed = True

    if changed:
        requests.post(url + "sendmetrics", data=json.dumps({name: value, "keep":keepCount, "self":{"name":self_name}}))
        print("Metrics sent:" + self_name + " - " + value)

    return
def cal_metrics(query_obj, MIND):
    return active_call_function(common_method(), query_obj["function"],cal_parameters(query_obj["parameters"], MIND))
def cal_parameters(params, MIND):
    ret_params = {}

    for key in params:
        if type(params[key]).__name__ == "dict":
            if params[key].get("query") is not None:
                ret_params[key]=cal_metrics(params[key]["query"], MIND)
            else:
                ret_params[key] = {}
                for key_item in params[key]:
                    if type(params[key][key_item]).__name__ == "dict":
                        ret_params[key][key_item] = cal_parameters(params[key][key_item], MIND)
                    else:
                        if type(params[key][key_item]).__name__ == "str":
                            ret_params[key][key_item] = get_from_context(params[key][key_item], MIND)
                        else:
                            ret_params[key][key_item] = params[key][key_item]
        else:
            ret_params[key]=get_from_context(params[key], MIND)
    return ret_params
def get_from_context(in_str, MIND):
    if str(in_str).startswith("@"):
        search_key = str(in_str)[1:]
        if MIND["@context"].get(search_key) is not None:
            return get_from_context(MIND["@context"][search_key], MIND)
        else:
            return in_str
    else:
        return in_str
def active_call_function(self,name,params):
    
    be_called_function = getattr(self, name)

    return be_called_function(params)
def upload_file(file_path, post_target):
    file = {"file":open(file_path,'rb')}
    response = requests.post(post_target, files=file)
    return response.text
def download_file(url,filename=None):
    if(not filename):
        filename=os.path.basename(url)
    leng=1
    while(leng==1):
        torrent=requests.get(url,stream=True)
        leng=len(list(torrent.iter_content(1024)))
        if(leng==1):
            print(filename,'download failed.')
            time.sleep(100)
        else:
            print(filename,'download completed.')

    with open(filename,'wb') as f:				
        for chunk in torrent.iter_content(1024):
            f.write(chunk)

    return
def process():
    global MIND
    global METRICS

    if MIND.get("messager") is None:
        # need to init the MIND, 1st to check local copy, then remote
        if os.path.exists("MIND.json"):
            MIND_updated = ""
            with open(os.sep.join(["MIND.json"]),'r')as file:
                for line in file.readlines():
                    MIND_updated += line
            MIND = json.loads(MIND_updated)
        else:
            print("MIND.json not found")
            return True

    response_mv = requests.get(MIND["messager"]["url"] + "metricsv?n=" + MIND["self"]["name"])
    if response_mv.text == "0":
        METRICS = {}

    requests.get(MIND["messager"]["url"] + "heart?n=" + MIND["self"]["name"])
    response = requests.get(MIND["messager"]["url"] + "readerv?n=" + MIND["self"]["name"])
    got_ts = float(response.text)

    if float(MIND["last"]) < got_ts:
        # if local MIND version is lower, update local MIND
        response = requests.get(MIND["messager"]["url"] + "reader?n=" + MIND["self"]["name"])
        MIND = json.loads(response.content)
        if MIND["stop"] == 1:
            return False
        print(time.strftime("%c") + ": local MIND upated.")

        if METRICS == {}:
            response = requests.get(MIND["messager"]["url"] + "metrics?n=" + MIND["self"]["name"])
            METRICS = json.loads(response.content)
            print(time.strftime("%c") + ": local METRICS upated.")
    else:
        if float(MIND["last"]) != got_ts:
            # if remote MIND version is lower, update remote MIND
            MIND_updated = ""
            with open(("MIND.json"),'r')as file:
                for line in file.readlines():
                    MIND_updated += line
            requests.post(MIND["messager"]["url"] + "sender", data=MIND_updated)

    # what do I have? & what to do?
    chk_owns(MIND["owns"], MIND,"", METRICS)

    if MIND["recurr"] != 1:
        return False

    return True

while True:
    try:
        if process():
            time.sleep(MIND["sleep"])
            print(time.strftime("%c") + ": Agent [" + MIND["self"]["name"] + "] is working...")
        else:
            break
    except Exception as e:
        print(str(e))
        time.sleep(10)