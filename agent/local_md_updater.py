import sys
import os
import ast
import json
import requests

def get_line_propertis(line):
    content_start = line.find("-")
    content_line = line[content_start+1:]
    left_line = line[:content_start]
    level = left_line.count("\t")

    if len(content_line) > 1:
        if content_line[len(content_line)-1] == "\n":
            content_line = content_line[:-1]

    return str(content_line).lstrip(),level
def findCurrentDataClass(currnt_line, tag):
    retline = ""
    ver_md = ""

    startIndex = currnt_line.find(tag)
    content_start = currnt_line.find("-")
    content_line = currnt_line[content_start+1:startIndex]
    left_line = currnt_line[:content_start]

    if currnt_line.find("#ver") > 0:
        ver_md = str(currnt_line[currnt_line.find("#ver")+4:]).replace("\n","").lstrip()
    currnt_class = ""
    #same level
    if content_line.rfind("]]") >= 0 and content_line.rfind("[[") >= 0:
        currnt_class = content_line[content_line.rfind("[[")+2:content_line.rfind("]]")]

        if ver_md == "":
            retline = currnt_line.replace(tag,"").rstrip() + "\n"
        else:
            retline = currnt_line

    return currnt_class, retline, left_line, ver_md
def get_data_lines(target_class_file, dataline_prefix,parentLine, ver_md):
    retLinesList = {}

    fullLines = []
    retVer = ""

    url_count = 0

    with open(target_class_file,'r', encoding="utf-8")as fp:
        for line in fp.readlines():
            fullLines.append(line)
            
    found = False
    line_index = 0
    for line_item in fullLines:
        if found:
            url = ""
            query = ""
            value = ""
            version = ""

            children_lines = get_children_lines(fullLines, line_index)
            for item in children_lines:
                if str(fullLines[line_index]).strip().find("[[url]]") >= 0:
                    url = str(item["line"])
                    for item_children in get_children_lines(fullLines, item["index"]):
                        if item_children["line"] == "[[query]]":
                            for item_url_children in get_children_lines(fullLines, item_children["index"]):
                                query = item_url_children["line"]
                        elif item_children["line"] == "[[value]]":
                            for item_url_children in get_children_lines(fullLines, item_children["index"]):
                                value = item_url_children["line"]
                        elif item_children["line"] == "[[ver]]":
                            for item_url_children in get_children_lines(fullLines, item_children["index"]):
                                version = item_url_children["line"]

                    if url != "":
                        retLinesList[url] = {}
                        retLinesList[url]["lines"] = []
                        retLinesList[url]["lines"].append(parentLine)
                        url_count += 1

                        if version != "":
                            response = requests.get(url + "&v=" + version)
                            ver_data = response.text
                            retLinesList[url]["ver"] = str(url_count) + ":" + str(ver_data)
                            retVer += retLinesList[url]["ver"] + ";"
                        else:
                            retLinesList[url]["ver"] = ""

                        if str(ver_md).find(retLinesList[url]["ver"] + ";") < 0:
                            response = requests.get(url)
                            current_obj = json.loads(response.content) 
                            
                            if query != "":
                                for item in query.split("."):
                                    if type(current_obj).__name__ == "str":
                                        current_obj = ast.literal_eval(current_obj)
                                    if current_obj.get(item) is not None:
                                        current_obj = current_obj[item]
                    
                            if value == "[[string]]":
                                retLinesList[url]["lines"].append(dataline_prefix + "\t- " + str(current_obj) + "\n")
                            else:
                                for item in current_obj:
                                    if value == "[[list]]":
                                        if type(item) is dict:
                                            chkDict = item
                                            for chk_key in chkDict:
                                                retLinesList[url]["lines"].append(dataline_prefix + "\t- " + str(chk_key) + "\n")
                                                retLinesList[url]["lines"].append(dataline_prefix + "\t\t- " + str(chkDict[chk_key]) + "\n")
                                        else:
                                            retLinesList[url]["lines"].append(dataline_prefix + "\t- " + str(item) + "\n")
                                    elif value == "[[dict]]":
                                        retLinesList[url]["lines"].append(dataline_prefix + "\t- " + str(item) + "\n")
                                        if type(current_obj[item]) is dict:
                                            chkDict = current_obj[item]
                                            for chk_key in chkDict:
                                                retLinesList[url]["lines"].append(dataline_prefix + "\t\t- " + str(chk_key) + "\n")
                                                retLinesList[url]["lines"].append(dataline_prefix + "\t\t\t- " + str(chkDict[chk_key]) + "\n")
                                        else:
                                            retLinesList[url]["lines"].append(dataline_prefix + "\t- " + str(current_obj[item]) + "\n")
                                    
        else:
            if line_item.find("[[Agent_Data]]") > 0:
                found = True

        line_index += 1

        # if retVer == "":
        #     retVer = ver_md
    return retLinesList, retVer
def remove_duplicated_lines(full_lines):
    retLines = []

    for item in full_lines:
        found = False
        for sub_item in retLines:
            if sub_item == item:
                found = True
                break
        
        if not found:
            retLines.append(item)
            # also append its children
    return retLines
def get_children_lines(full_lines, target_line_index):
    ret = []
    line_index = 0

    if len(full_lines) > target_line_index:
        parent_content_line,parent_level = get_line_propertis(full_lines[target_line_index])
        target_level = parent_level + 1

        line_index = target_line_index + 1

        for item in full_lines[target_line_index+1:]:
            if not chkIsNormalLine(item):
                line_index += 1
                continue

            content_line,level = get_line_propertis(item)

            if level != (parent_level + 1):
                if level < target_level:
                    return ret

                line_index += 1
                continue

            if level == target_level:
                ret.append({"line":content_line,"index":line_index,"level":level})

            line_index += 1

    return ret
def process_md(target_file, tag_data):
    # replace mark
    if os.path.isfile(target_file) :
        parent_folder = os.path.dirname(target_file) + os.sep
        itemFullPath = target_file

        allLineList = []
        addingLineList = []
        existingChildrenList = []

        lineCount = 0
        dataLinesWrittenCount = 0

        currentDataClass = ""

        fullLines = []
        chk_fullLInes = []
        
        with open(itemFullPath,'r', encoding="utf-8")as fp:
            for line in fp.readlines():
                fullLines.append(line)
                chk_fullLInes.append(line)

        for line in fullLines:
            if line.find(tag_data) >= 0:
                currentDataClass,addLine,datalineprefix,ver_md = findCurrentDataClass(fullLines[lineCount], tag_data)
                #fill data
                if currentDataClass != "":
                    target_class_file = parent_folder + currentDataClass + ".md"
                    if os.path.isfile(target_class_file) :
                        # check all children lines
                        dataLines, dataVerSub = get_data_lines(target_class_file, datalineprefix,line,ver_md)
                        # rewrite class line with data version
                        if dataVerSub != "":
                            if str(fullLines[lineCount]).find("#ver") > 0:
                                fullLines[lineCount] = addLine[:addLine.find("#ver")+4] + " " + dataVerSub + "\n"
                            else:
                                if fullLines[lineCount][-1] != "a":
                                    fullLines[lineCount] = fullLines[lineCount][:-1] + " #ver" + " " + dataVerSub + "\n"
                                else:
                                    fullLines[lineCount] = fullLines[lineCount] + " #ver" + " " + dataVerSub + "\n"

                        if len(dataLines) > 0:
                            for dataLine in dataLines:
                                existingChildrenList = get_children_lines(chk_fullLInes, lineCount)
                                dataChildrenList = get_children_lines(dataLines[dataLine]["lines"], 0)

                                for add_item in mapDataToExsiting(lineCount, existingChildrenList, chk_fullLInes, dataChildrenList, dataLines[dataLine]["lines"]):
                                    addingLineList.append(add_item)

                                if len(addingLineList) > 0:
                                    dataLinesWrittenCount = len(addingLineList)

                                for chk_item in dataLines[dataLine]["lines"]:
                                    chk_fullLInes.append(chk_item)
                else:
                    print("Class not found on line: " + line)
            lineCount += 1

        if dataLinesWrittenCount > 0:
            # getting writting list ready
            chkIndex = 0
            for item in fullLines:
                if item[-1:] != "\n":
                    allLineList.append(item + "\n")
                else:
                    allLineList.append(item)

                #property line is not a line need to count
                if chkIsNormalLine(item):
                    for addItem in addingLineList:
                        if addItem["target_index"] == chkIndex:
                            # see if next line is not Normal, if yes, skip this line
                            if len(fullLines) > chkIndex + 1:
                                if not chkIsNormalLine(fullLines[chkIndex + 1]):
                                    addItem["target_index"] += getPropertyLineCount(fullLines, chkIndex) + 1
                                else:
                                    allLineList.append(addItem["line"])
                            else:
                                allLineList.append(addItem["line"])
                chkIndex += 1

            writeAllLine(target_file, allLineList)
            print(str(dataLinesWrittenCount) + " DATA line(s) written to " + target_file)
        else:
            print("No changes to " + target_file)
def getPropertyLineCount(fullLines, lineIndex):
    retCount = 0

    while len(fullLines) > lineIndex + 1:
        lineIndex += 1
        if not chkIsNormalLine(fullLines[lineIndex]):
            retCount += 1
        
    return retCount
def chkIsNormalLine(line):
    content, level = get_line_propertis(line)

    if str(line)[level].find("-") == 0:
        return True
    
    return False
def mapDataToExsiting(target_index, existingChildrenList, existingFullList, dataChildrenList, dataFullList):
    retList = []

    for item in dataChildrenList:
        found = False
        for e_item in existingChildrenList:
            if item["line"] == e_item["line"] and item["level"] == e_item["level"]:
                found = True
                # check children and merge
                for add_item in mapDataToExsiting(e_item["index"], get_children_lines(existingFullList, e_item["index"]), existingFullList, get_children_lines(dataFullList, item["index"]), dataFullList):
                    retList.append(add_item)
                break

        if not found:
            prefix = ""
            p_count = 0
            while p_count < item["level"]:
                prefix += "\t"
                p_count += 1

            retList.append({"line": prefix + "- " + item["line"] + "\n", "target_index":target_index})
            for notExsitingItem in getAllChildren(dataFullList, item["index"]):
                retList.append({"line": notExsitingItem, "target_index":target_index})

    return retList
def getAllChildren(fullList, targetIndex):
    retList = []

    childrenLines = get_children_lines(fullList, targetIndex)

    if len(childrenLines) > 0:
        for item in childrenLines:
            prefix = ""
            p_count = 0
            while p_count < item["level"]:
                prefix += "\t"
                p_count += 1
            retList.append(prefix + "- " + item["line"] + "\n")
            for retItem in getAllChildren(fullList, item["index"]):
                retList.append(retItem)
    else:
        return []

    return retList
def getTypeString(line, findStrStart, findStrEnd):
    endIndex = []
    startIndex = []
    lineLength = len(line)
    findIndexStart = 0

    endFoundIndex = str(line).find(findStrEnd, findIndexStart)
    while endFoundIndex > -1:
        endIndex.append(endFoundIndex)
        if (len(findStrEnd) + endFoundIndex) < lineLength:
            findIndexStart = len(findStrEnd) + endFoundIndex
            endFoundIndex = str(line).find(findStrEnd, findIndexStart)
        else:
            break

    retList = []
    # find nearest start flag for every "endIndex"
    for item in endIndex:
        sIndex = 0
        maxIndex = 0
        while maxIndex <= item:
            foundS = str(line).find(findStrStart, sIndex)
            if foundS > -1 and foundS < item:
                maxIndex = str(line).find(findStrStart, sIndex)
            else:
                break
            sIndex = maxIndex
            sIndex += len(findStrStart)
        retList.append(str(line)[maxIndex+len(findStrStart):item])

    return retList
def writeAllLine(path, lines):
    with open(path,'w', encoding="utf-8")as fp:
        for item in lines:
            fp.write(item)
    return
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        md_target = sys.argv[1]
        md_target_list = ast.literal_eval(md_target)

        for item in md_target_list:
            process_md(item, "#Agent_Data")

    #test_str = "['D:\\\\SynologyDrive\\\\Note\\\\AutoGL\\\\pages\\\\Hub.md', 'D:\\\\SynologyDrive\\\\Note\\\\AutoGL\\\\pages\\\\NotePersonList.md']"
    # test_str = "['D:\\\\SynologyDrive\\\\Note\\\\AutoGL\\\\pages\\\\Hub.md']"
    # md_target_list = ast.literal_eval(test_str)

    # for item in md_target_list:
    #     process_md(item, "#Agent_Data")