from collections import defaultdict
import os
import re
from time import sleep
from datetime import datetime, timedelta
from collections import defaultdict
import random
import time

class BallData:
        ID = 0
        date = ''
        red = []
        blue = 0
        duplicates_red = {}
        duplicates_blue = {}

        def __init__(self, ID, date, red, blue):
            self.ID = ID
            self.date = date
            self.red = red
            self.blue = blue
        def __lt__(self, other):
            return (self.ID) < (other.ID)

def create_ball_data_from_string(data_str):
   
    match = re.match( r'(\d+)\s(\d{4}-\d{2}-\d{2})\s\[(\d+(?:,\s\d+)*)\]--\[(\d+)\]', data_str)
    if match:
        ID = int(match.group(1))
        date = match.group(2)
        red = [int(num) for num in match.group(3).split(',')]
        blue = int(match.group(4))
        return BallData(ID, date, red, blue)
    else:
        return None

def remove_chinese_chars(input_str):
    # 使用正则表达式匹配中文字符
    chinese_pattern = re.compile("[\u4e00-\u9fa5（）]+")
    # 使用 sub 方法替换中文字符为空字符串
    result = chinese_pattern.sub('', input_str)
    
    return result


def LoadFile(fileName):
    AllDataMap ={}
    with open(fileName, 'r',encoding="utf-8") as file:
        content = file.readlines()
    
    for line in content:
        if 'recommend' in line or line == '\n':
            continue

        data = create_ball_data_from_string(line)
        AllDataMap[data.ID] =data
    file.close()
    return AllDataMap





def GetFileDate(dateStr):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'OutPut')
    fileName = os.path.join(output_dir, 'BallData.txt')
    AllDataMap = LoadFile(fileName)

    keys_to_delete = []
    startDate = datetime.strptime(dateStr,'%Y-%m-%d')
    for key, value in AllDataMap.items():
        date = datetime.strptime(value.date,'%Y-%m-%d')
        if date < startDate:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del AllDataMap[key]
    return AllDataMap