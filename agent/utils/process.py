def fengkong_market_down(param):
    ret = {}
    ret_list = []
    data_list = param["input_a"]["data"]["records"]

    for item in data_list:
        ret_list.append({
            "time": item["alarmDate"], 
            "ys": '货值跌幅预警', 
            "tz": '市场下行预警数', 
            "desc": item["alarmDesc"], 
            "status": 1, 
            "company": item["organizeName"],
            "link": 'https://op.xinyilian.com/wind/earlyWarningCenter/earlyWarningMessageList'})

    ret = {
        "code": "scjg",
        "label": "市场价格风险",
        "legend": [
            {
                "label": "要素",
                "value": ["代理风险"]
            },
            {
                "label": "体征指标",
                "value": ["市场下行预警数", "保证金比例预警数", "代理逾期库存量"]
            },
            {
                "label": "数据来源",
                "value": ["供服系统"]
            },
            {
                "label": "管控模型",
                "value": ["代理风险预警模型"]
            }
        ],
        "yjsjsmzq": {
            "current": 0,
            "overtime": 0
        },
        "yjxq": ret_list
    }

    return ret 
def fengkong_margin_level(param):
    ret = {}
    return {}