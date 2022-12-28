import os
def select_md(param):
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