#import numpy
import json
import requests
import time
import os
import importlib
import utils.common_method

# import pandas as pd
# from pyhive import hive

global MIND
global METRICS
MIND = {}
METRICS = {}

def upate_mind():
    global MIND
    print(time.strftime("%c") + ": " + requests.post(MIND["messager"]["url"] + "sender", json=MIND))
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
                    write_metrics(path_prefix + "." + item_metrics["name"], cal_metrics(item_metrics["query"], MIND), MIND["messager"]["url"], METRICS,MIND["@context"]["self_name"], keepCount)

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
        latest_value = METRICS[name]
        # if just got from remote, this should be a list
        if type(METRICS[name]).__name__ == "list":
            if len(METRICS[name]) > 0:
                if type(METRICS[name][-1]).__name__ == "dict":
                    if METRICS[name][-1].get("value") is not None:
                        latest_value = METRICS[name][-1]["value"]
                        METRICS[name] = latest_value

        if latest_value != value and str(value).strip() != "":
            METRICS[name] = value
            changed = True
    else:
        if str(value).strip() != "":
            METRICS[name] = value
            changed = True

    if changed:
        requests.post(url + "sendmetrics", json={name: value, "keep":keepCount, "self":{"name":self_name}})
        print("Metrics sent: " + self_name + " - " + str(value))
    else:
        print("No changes for: " + name)

    return
def cal_metrics(query_obj, MIND):
    if query_obj.get("class") is not None:
        if query_obj.get("function") is not None:
            if importlib.util.find_spec(query_obj["class"]) is not None:
                new_module = importlib.import_module(query_obj["class"])
                importlib.reload(new_module)
                return active_call_function(new_module, query_obj["function"],cal_parameters(query_obj["parameters"], MIND))
            else:
                print("Class [" + str(query_obj["class"]) + "] not found.")
        else:
            print("Function not specified in Class [" + query_obj["class"] + "].")
            return {}
    else:
        if query_obj.get("function") is not None:
            return active_call_function(utils.common_method, query_obj["function"],cal_parameters(query_obj["parameters"], MIND))
        else:
            print("Function [" + str(query_obj["function"]) + "] not found in Common methods.")
            return {}
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
def active_call_function(import_class,func_name,params):
    # check if class exits, if not found, import dynamicly
    if hasattr(import_class, func_name):
        be_called_function = getattr(import_class, func_name)
        return be_called_function(params)
    else:
        print("Function ["+ func_name +"] not found in " + import_class.__name__)
        return {}
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
            with open(os.sep.join(["MIND.json"]),'r')as file:
                MIND = json.load(file)
        else:
            print("MIND.json not found")
            return True

    self_name = MIND["@context"]["self_name"]
    messager_url = MIND["messager"]["url"]

    response_mv = requests.get(messager_url + "metricsv?n=" + self_name)
    if response_mv.text == "0":
        METRICS = {}

    requests.get(messager_url + "heart?n=" + self_name)
    response = requests.get(messager_url + "readerv?n=" + self_name)
    got_ts = float(response.text)

    if float(MIND["last"]) < got_ts:
        # if local MIND version is lower, update local MIND
        response = requests.get(messager_url + "reader?n=" + self_name)
        MIND = json.loads(response.content)
        if MIND["stop"] == 1:
            return False
        print(time.strftime("%c") + ": local MIND upated.")

        if METRICS == {}:
            response = requests.get(messager_url + "metrics?n=" + self_name)
            METRICS = json.loads(response.content)
            print(time.strftime("%c") + ": local METRICS upated.")
    else:
        if float(MIND["last"]) != got_ts:
            # if remote MIND version is lower, update remote MIND
            MIND_updated = {}
            with open(("MIND.json"),'r')as file:
                MIND_updated=json.load(file)

            requests.post(messager_url + "sender", json=MIND_updated)

    # what do I have? & what to do?
    chk_owns(MIND["owns"], MIND,"", METRICS)

    if MIND["recurr"] != 1:
        return False

    return True

while True:
    try:
        if process():
            time.sleep(MIND["sleep"])
            print(time.strftime("%c") + ": Agent [" + MIND["@context"]["self_name"] + "] is working...")
        else:
            break
    except Exception as e:
        print(str(e))
        time.sleep(10)