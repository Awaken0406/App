import os
import sys
from selenium import webdriver
from time import sleep
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from lxml import etree
import re
from selenium.webdriver.common import by
from datetime import datetime, timedelta
from collections import defaultdict
import time
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BallData:
     ID = ''
     date = ''
     red = []
     blue = []
     hit = 0
     hitAdd = 0


     def __init__(self, ID, date, red, blue):
            self.ID = ID
            self.date = date
            self.red = red
            self.blue = blue

     def __lt__(self, other):
            return (self.ID) < (other.ID)

    
 
def PrintResult(BallDataMap):
     with open(f'./OutPut/DaLeTouData.txt', "w",encoding="utf-8") as file:
          for data in BallDataMap.values():
               #info = f'期数:{data.ID},时间:{data.date},前区:{data.front},后区:{data.after},基本注数:{data.hit},追加注数:{data.hitAdd}'
               info = f'{data.ID} {data.date} {data.red}--{data.blue}'
               #print(info)
               file.write(info+'\n')
     file.close()
      


def ParseSource(BallDataMap,html): 
    dataList = html.xpath('//*[@id="historyData"]/tr')
    tempDate = datetime.now().date()
    skip_remaining = False
    for data in dataList:



         if skip_remaining == True:
               skip_remaining = False
               continue
    
         
         text = data.xpath('.//text()')
         if text[0] == '派奖':
               skip_remaining = True
               continue
         ball = BallData(0,'',[],[])
         ball.red = []
         ball.blue = []
         ball.ID = int(text[0])
         ball.date = text[1]

         if text[2] == '派奖':
               skip_remaining = True
               continue

         for i in range(2,7):
              ball.red.append(int(text[i]))
         ball.blue.append(int(text[7]))
         ball.blue.append(int(text[8]))
         #ball.hit = int(text[9])
         #ball.hitAdd = int(text[11])
         BallDataMap[ball.ID] = ball
         tt = datetime.strptime(ball.date,'%Y-%m-%d').date()
         if tt < tempDate:
              tempDate = tt 
    return tempDate

def create_ball_data_from_string(data_str):
   
    match = re.match(  r'(\d+)\s+(\d{4}-\d{2}-\d{2})\s+\[([\d, ]+)\]\-\-\[([\d, ]+)\]', data_str)
    if match:
          # 提取字段
          ID = int(match.group(1))  # 提取 ID 并转换为整数
          date = match.group(2)     # 提取日期
          red = [int(num) for num in match.group(3).split(',')]  # 提取 red 列表并转换为整数列表
          blue = [int(num) for num in match.group(4).split(',')]  # 提取 blue 列表并转换为整数列表
          return BallData(ID, date, red, blue)
    else:
        return None

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
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 如果是普通的 Python 脚本
        base_path = os.path.dirname(os.path.abspath(__file__))
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_path, 'OutPut')
    fileName = os.path.join(output_dir, 'DaLeTouData.txt')    
    AllDataMap = LoadFile(fileName)
    #print("GetFileDate",base_path)

    keys_to_delete = []
    startDate = datetime.strptime(dateStr,'%Y-%m-%d')
    for key, value in AllDataMap.items():
        date = datetime.strptime(value.date,'%Y-%m-%d')
        if date < startDate:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del AllDataMap[key]
    return AllDataMap

if __name__ == "__main__":
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'OutPut')
    fileName = os.path.join(output_dir, 'DaLeTouData.txt')
    BallDataMap = LoadFile(fileName)
    
    option = ChromeOptions() 
    #option.add_argument('--headless')
    # 禁用"Chrome正受到自动测试软件控制"的提示
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    # 覆盖navigator.webdriver属性，通常用于被检测
    option.add_argument("--disable-blink-features=AutomationControlled")

    browser = webdriver.Chrome(option)
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    #browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',{'source' : 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'})
    #browser.set_window_size(1366,768)
    #browser.maximize_window()
    browser.get('https://www.lottery.gov.cn/kj/kjlb.html?dlt')
    sleep(2)
 
    startDate = '2025-02-05'
    start = datetime.strptime(startDate,'%Y-%m-%d').date()

    #child_frame = browser.find_element(by.By.XPATH,'//*[@id="iFrame1"]')
    #browser.switch_to.frame(child_frame)
     # 等待 iframe 加载完成
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "iFrame1"))
    )

    # 找到 iframe 元素
    iframe = browser.find_element(By.ID, "iFrame1")

    # 切换到 iframe
    browser.switch_to.frame(iframe)
    while True:
          sleep(1)

          html =etree.HTML(browser.page_source)
          #print(html.xpath("//text()"))
          tt = ParseSource(BallDataMap,html)
          if tt <= start:
               break
          nextBtn = browser.find_element(by.By.XPATH,'/html/body/div/div/div[3]/ul/li[13]')
          nextBtn.click()
    BallDataMap = dict(sorted(BallDataMap.items(), key=lambda x: x[1]))
    PrintResult(BallDataMap)
