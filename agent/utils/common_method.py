import json
import socket
import requests
import os
import subprocess
import ast

def select(param):
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
def get_from_web(param):
    params = ""
    if param.get("get_param") is not None:
        for item in param["get_param"]:
            if params == "":
                params = "?" + str(item) + "=" +  str(param["get_param"][item])
            else:
                params += "&" + str(item) + "=" + str(param["get_param"][item])
    
    if param.get("metrics_address") is not None:
        response = requests.get(param["metrics_address"]["url"] + params)
        return json.loads(response.content) 
    
    return {}
def request_post(param):
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
def request_get(param):
    if param.get("args") is not None:
        response = requests.get(**param["args"])
        return response.text

    return {}
def excute_py(param):
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
def json_count(param):
    ret = 0

    target = {}
    if type(param["input_json"]).__name__ == "str":
        target = json.loads(param["input_json"])
    else:
        target = param["input_json"]

    if target.get(param["count_name"]) is not None:
        ret = len(target[param["count_name"]])

    return ret
def json_convert_from_str(param):
    target = str(param["target"]).replace("'",'"')
    return json.loads(target)
def get_home_dir(param):
    return os.getcwd()
def get_dir_files(param):
    ret = []
    if os.path.exists(param["path"]["value"]):
        for f in os.listdir(param["path"]["value"]):
            if os.path.isfile(os.sep.join([param["path"]["value"],f])):
                ret.append(f)
    return ret
def get_dir_folders(param):
    ret = []
    if os.path.exists(param["path"]["value"]):
        for f in os.listdir(param["path"]["value"]):
            if os.path.isdir(os.sep.join([param["path"]["value"],f])):
                ret.append(f)
    return ret
def get_parent_folder(param):
    ret = ""
    if os.path.exists(param["path"]["value"]):
        ret = os.path.abspath(os.path.dirname(param["path"]["value"]))
    return ret
def get_join_path(param):
    ret = ""
    if os.path.exists(os.sep.join([param["path_a"]["value"],param["path_b"]["value"]]) ):
        ret = os.path.abspath(os.sep.join([param["path_a"]["value"],param["path_b"]["value"]]))
    return ret
def get_ip(param):
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
def exe_file(param):
    if param.get("app") is not None:
        if param.get("param") is not None:
            os.system(str(param["app"]["value"]) + " " + str(param["param"]["value"]))
        else:
            os.system(str(param["app"]["value"]))
    return