import math
from time import sleep

from datetime import datetime, timedelta
from collections import defaultdict
import random
import time
import Selenium_Ball_Update
import Selenium_Recommend_Analyse
import hashlib
import string
from collections import defaultdict, OrderedDict
import csv
#import mysql_db as db
import secrets




BallArray = [(1, 2, 2, 1), (2, 2, 1, 1), (2, 1, 2, 1), (2, 2, 2, 0), (1, 3, 1, 1),
(4, 1, 1, 0), (1, 3, 2, 0), (1, 2, 3, 0), (1, 1, 3, 1), (1, 4, 1, 0),
(0, 3, 2, 1), (3, 1, 2, 0), (3, 2, 1, 0), (2, 1, 3, 0), (1, 4, 0, 1),
(2, 3, 1, 0), (3, 2, 0, 1), (3, 1, 1, 1), (2, 1, 1, 2)]



'''
在 Python 中，类的数据成员（类属性）在类定义中被初始化为可变对象（如列表）时，
这些对象会被所有该类的实例共享。这可能导致在实例化新对象时，类属性的可变对象并不会被重置为空，
而是保留了上一个实例的值。
'''


def Analyse(sliced_list):
     RedTotalTimes = defaultdict(int)
     BlueTotalTimes = defaultdict(int)
     nearNum = 5
   
     for i in range(len(sliced_list)):#默认升序
          ball = sliced_list[i]
          id = 0
          ball.duplicates_red = {}
          for num in range(i+1,i+1+nearNum):
                    if(num >= len(sliced_list)):
                         break
                    id += 1
                    set1 = set(ball.red)
                    set2 = set(sliced_list[num].red)
                    duplicates = set1.intersection(set2)
                    if len(duplicates) > 0:
                         ball.duplicates_red[id] = list(duplicates)

     blueExistCount = 0
     for i in range(len(sliced_list)):
          ball = sliced_list[i]
          id = 0
          ball.duplicates_blue = {}
          for num in range(i+1,i+1+nearNum):
                    if(num >= len(sliced_list)):
                         break
                    id += 1
                    if ball.blue == sliced_list[num].blue:
                         ball.duplicates_blue[id] = ball.blue
                         blueExistCount += 1
     
     redNum = defaultdict(int)
     redTimes = defaultdict(int)
     blueTimes = defaultdict(int)
     for data in sliced_list:    
          for k,numList in data.duplicates_red.items():
               redNum[len(numList)]+=1
               redTimes[k]+=1
          for k,numList in data.duplicates_blue.items():
               blueTimes[k]+=1

          #print(f'ID:{data.ID},date:{data.date},red:{data.red},blue:[{data.blue}]')
          #print('red',data.duplicates_red)
          #print('blue',data.duplicates_blue)
     
          for num in data.red:
               RedTotalTimes[num] += 1
          if isinstance(data.blue, list):
               for b in data.blue:
                    BlueTotalTimes[b] += 1
          else:
               BlueTotalTimes[data.blue] += 1
     #print(f'Total:{len(sliced_list)},blueExistCount:{blueExistCount}')
     RedTotalTimes = sorted(RedTotalTimes.items(), key=lambda x: x[1], reverse=True)
     BlueTotalTimes = sorted(BlueTotalTimes.items(), key=lambda x: x[1], reverse=True)

     len1 = 25
     len2 = int(len(BlueTotalTimes)/2)
     index1 = 0
     index2 = 0

     redTopKeys = []
     blueTopKeys = []
     for num, count in RedTotalTimes: 
          index1+=1
          if index1 > len1:
               break
          redTopKeys.append(num)
     for num, count in BlueTotalTimes: 
          index2+=1
          if index2 > len2:
               break
          blueTopKeys.append(num)

     #print(f'total:{len(sliced_list)},nearNum:{nearNum},redNum:{redNum},redTimes:{redTimes},blueTimes:{blueTimes}')
     #print("RedTotalTimes:",RedTotalTimes)
     #print("BlueTotalTimes:",BlueTotalTimes)
     #print("redTopKeys:",redTopKeys)     
     #print("blueTopKeys:",blueTopKeys)
     return redTopKeys,blueTopKeys
   

def DoCombinationAnalyse(number,red,Array):
     if len(Array) == 0:
          return True
     numList  =[0,0,0,0]
     #0,10,20,30
     for num in red:
            i = int(num / 10)
            numList[i] += 1

     #十位还是各位
     index = int(number / 10)

     for data in Array:
          if numList[index] < data[index]:
               ret = True
               for i in range(len(data)):
                    if numList[i] > data[i]:
                         ret = False
               if ret == True:
                    return True
                    
     return False


# 生成随机字符串
def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def RecommendRed(RandType,isCheck,isDaLeTou,redMax,redTopKeys, count,CombArray):
     recommend_red = []
     while True:
               if(len(recommend_red) >= count):
                    break
         
               num = enhanced_random(RandType,redMax)
               if num not in recommend_red:
                    if isCheck:
                         isOK = DoCombinationAnalyse(num,recommend_red,CombArray)
                         if isOK == False:
                              continue                                
                    if num in redTopKeys:                     
                         recommend_red.append(num)    
                                   
     return recommend_red


def DoRecommend(RandType,isHorse,isCheck,isDaLeTou,redTopKeys,blueTopKeys,recommendCount,isPrint,isWrite,CombArray):
     continuous = True
     if isDaLeTou:
          G_exRed = 5
          G_exBlue = 2
          redMax = 35
          blueMax = 12
     else:
          G_exRed = 6
          G_exBlue = 1
          redMax = 33
          blueMax = 16

     if isHorse:
          G_exRed = 6
          G_exBlue = 1
          redMax = 49
          blueMax = 49
 

     

     recommend_red = []
     recommend_blue = []
     current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

     AllDataList = []



     for i in range(recommendCount):
          recommend_red = []
          recommend_blue = []
          
          recommend_red = RecommendRed(RandType,isCheck,isDaLeTou,redMax,redTopKeys,G_exRed,CombArray)      
          #blue
          while True: 
               if(len(recommend_blue) == G_exBlue):
                         break
               num = enhanced_random(RandType,blueMax)
               if num not in recommend_blue:
                    if num in blueTopKeys:
                         recommend_blue.append(num)


          recommend_red.sort()
          #recommend_blue.sort()
          if isPrint == True:
               print(f"{recommend_red}--{recommend_blue}")

          dd = Selenium_Recommend_Analyse.DataList()
          dd.front = recommend_red
          dd.back = recommend_blue
          AllDataList.append(dd)

     if isWrite == True: 
          db.SaveBall(AllDataList)

          '''file = open(fileName, "w",encoding="utf-8") 
          file.write(f'recommend:{current_time_str}\n')
          for d in AllDataList:    
               file.write(f"{d.front}--{d.back}\n")
          file.write("\n")
          file.close()'''
     return AllDataList



def PrintResult(isShuffle,isHorse,Array,isCheck,isDaLeTou,fileName,RedMap,BlueMap,ID,RMap,BMap,loopTimes,recommendCount,isPrint):
     
     redList = RMap[ID]
     blueList = BMap[ID]
     if isShuffle :
          random.shuffle(redList)
          random.shuffle(blueList)

    
     if isDaLeTou:
          redNum = 5
          blueNum = 2
     else:
          redNum = 6
          blueNum = 1
     file = open(fileName, "a",encoding="utf-8") 
     if False:

          #info = f'date:{current_time_str},loopTimes:{loopTimes},recommendCount:{recommendCount},ID:{ID},red index:{redList},blue index:{blueList}\n'
          #file.write(info)
          #print(info, end='')

          index = 0
          strinfo =''
          redDataList = []
          blueDataList = []
          for k,v in RedMap.items():
               index+=1
               redDataList.append({"index":index,"number":k,"count":v})
          #输出表格
          strinfo = OutputTable(redDataList)
          #print(strinfo)
          #file.write(f'{strinfo}\n')

          # 保存 redDataList 到 CSV 文件
          save_red_data_to_csv(isDaLeTou,redDataList)

          index = 0
          for k,v in BlueMap.items():
               index += 1
               blueDataList.append({"index":index,"number":k,"count":v})
          #输出表格
          #strinfo = OutputTable(blueDataList)    
          #print(strinfo)
          #file.write(f'{strinfo}\n')
          #file.write("\n")
    
     outRed = []
     outBlue =[]
     for idIndex in redList:
          index =0
          for k,v in RedMap.items():
               index += 1
               if index == idIndex:
                    if isCheck:#输出comb
                        if DoCombinationAnalyse(k,outRed,Array):
                              outRed.append(k)
                    else:
                         outRed.append(k)
                    break
          if len(outRed) >= redNum:
               break

     for idIndex in blueList:
          index =0
          for k,v in BlueMap.items():
               index += 1
               if index == idIndex:
                    outBlue.append(k)
                    break
          if len(outBlue) >= blueNum:
               break    
     #if not isHorse:         
     #     outRed.sort()
     #     outBlue.sort()
     if isPrint:
          current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
          print('-----------------------')
          file.write(f'-----------------------\n')
          file.write(f'date:{current_time_str},ID:{ID},loopTimes:{loopTimes},recommendCount:{recommendCount}\n')
          print(f'date:{current_time_str},ID:{ID},loopTimes:{loopTimes},recommendCount:{recommendCount}')
          print(f'{outRed}--{outBlue}')
          print('-----------------------')
          file.write(f'{outRed}--{outBlue}\n')
          file.write(f'-----------------------\n')
          file.write(f'\n')
     file.close()

     return outRed,outBlue

def Doit(isHorse,isDaLeTou,ID,fileName,Array,BallDataList,recommendCount,loopTimes
         ,redTopKeys,blueTopKeys,cfgData,isPrint):
     RedMap = defaultdict(int)
     BlueMap = defaultdict(int)
     isFixed= cfgData.FixedMap[ID]
     isCheck = cfgData.CheckMap[ID]
     RandType = cfgData.RandType[ID]
     
     for t in range(loopTimes):
          seed = GetTodayRandomTime()
          if isFixed:
               random.seed(88888888)
          else:
               random.seed(seed)
          
          AllDataList = DoRecommend(RandType,isHorse,isCheck,isDaLeTou,redTopKeys,blueTopKeys,recommendCount,False,False,Array)
          for i in range(len(AllDataList)):
               info  = AllDataList[i]
               BlueMap[info.back[0]] += 1
               if isDaLeTou :
                    BlueMap[info.back[1]] += 1

               for d in range(len(info.front)):
                    num = info.front[d]
                    RedMap[num] += 1

     RedMap = dict(sorted(RedMap.items(), key=lambda x: x[1], reverse=True))
     BlueMap = dict(sorted(BlueMap.items(), key=lambda x: x[1], reverse=True))
     outRed,outBlue = PrintResult(False,isHorse,Array,isCheck,isDaLeTou,fileName,RedMap,BlueMap,ID,cfgData.RMap,cfgData.BMap,loopTimes,recommendCount,isPrint)
     return outRed,outBlue

def GetTodayRandomTime():
     now = datetime.now()
     today = datetime(now.year, now.month, now.day)
     timestamp = today.timestamp()
     rand = random.randint(43200, 86400)
     return timestamp + rand


def GetRandomTimestamp(date_string):
     #date_string = '2022-01-01'
     timestamp = datetime.strptime(date_string, '%Y-%m-%d').timestamp()
     rand = random.randint(43200, 86400)
     return timestamp + rand

def GetZeroTimeStamp(date_string):
     #date_string = '2022-01-01'
     timestamp = datetime.strptime(date_string, '%Y-%m-%d').timestamp()
     return timestamp

def Get12HourTimeStamp(date_string):
     #date_string = '2022-01-01'
     timestamp = datetime.strptime(date_string, '%Y-%m-%d').timestamp()
     return timestamp + 43200

def GetToday12HourTimeStamp():
     now = datetime.now()
     today = datetime(now.year, now.month, now.day)
     timestamp = today.timestamp()
     return timestamp + 43200
     


def RegID(cfgData):
    
     #稳，第二遍比较稳
     cfgData.RMap[1001] = [15,12,26,8,21,5,14,23]
     cfgData.BMap[1001] = [15,6,13]
     cfgData.FixedMap[1001] = False
     cfgData.CheckMap[1001] = True
     cfgData.RandType[1001] = 1

     cfgData.RMap[1002] = [30, 1, 26, 25, 24, 29, 27, 31]
     cfgData.BMap[1002] = [15, 5, 2]
     cfgData.FixedMap[1002] = False
     cfgData.CheckMap[1002] = True
     cfgData.RandType[1002] = 2


     #最新
     
     cfgData.RMap[1003] = [25,24,3,2,1,5,4,6,7,8,9,22,11,23,10,12,21,13,20,14,19,18,17,15,16]
     cfgData.BMap[1003] = [5, 4, 3, 2, 1, 6, 7]


     #cfgData.RMap[1003] = [25,24,5,4,3,2,1,23,6,7,10,8,9,11,12,13,22,14,15,17,16,20,21,19,18]
     #cfgData.BMap[1003] = [2, 3, 1, 4, 6, 5, 7, 8]
     #cfgData.RMap[1003] = [25,24,23,22,20,21,18,17,19,16,15,13,12,14,4,11,10,3,9,5,8,2,7,1,6]
     #cfgData.BMap[1003] = [2,1,4,3,5,6]
     cfgData.FixedMap[1003] = False
     cfgData.CheckMap[1003] = True
     cfgData.RandType[1003] = 1







     

#从推荐中选择
def SelectRecommend(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,
               redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap):
     
     if isDaLeTou:
          redCount = 5
          blueCount = 2
     else:
          redCount = 6
          blueCount = 1

     red=[]
     blue = []
     rList = []
     bList = []
     for i in range(5): 
        
        r,b =  Doit(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,
               redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap,False)
        red += r
        blue += b
        rList.append(r)
        bList.append(b)
        sleep(5)

     current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
     red = list(set(red))
     blue = list(set(blue))
     file = open(name, "a",encoding="utf-8") 
     file.write(f'------------SelectRecommend------------\n')
     file.write(f'ID:{ID},date:{current_time_str}\n')
     print(f'------------SelectRecommend------------ID:{ID}')
     print(f'rednumberList:{red}')
     print(f'bluenumberList:{blue}')
     file.write(f'rednumberList:{red}\n')
     file.write(f'bluenumberList:{blue}\n')
     file.write(f'\n')
     #打乱数组
     #random.shuffle(red)
     #random.shuffle(blue)
     index = 0
     file.write(f'Recommend:\n')   
     print(f'Recommend:')
     for r in rList:
          file.write(f'{r}--{bList[index]}\n')   
          print(f'{r}--{bList[index]}')
          index += 1

     file.write(f'Select:\n')   
     print(f'Select:')
     for i in range(5):
          recommend_red = []
          recommend_blue = []
          for i in range(blueCount):
               recommend_blue.append(random.choice(blue))
          while True:
               num = random.choice(red)
               #isOk =  DoCombinationAnalyse(num,recommend_red,BallArray)
               isOk = True
               if isOk and num not in recommend_red:
                    recommend_red.append(num)
               if len(recommend_red) == redCount:
                    break
          recommend_red.sort()
          recommend_blue.sort()
          print(f'{recommend_red} -- {recommend_blue}')
          file.write(f'{recommend_red} -- {recommend_blue}\n')
     file.write(f'----------------------------------------\n\n')
     file.close()


def OutputTable(dataList):

     fields = ["index", "number", "count"]

     # 生成转置后的数据行
     rows = []
     for field in fields:
          row = [field]  # 首列为字段名称
          for entry in dataList:
               row.append(str(entry[field]))
          rows.append(row)

     # 生成列标题
     headers = ["Field"] + [f"Data{i+1}" for i in range(len(dataList))]

     # 计算列宽
     max_widths = []
     # 首列宽度（字段名称列）
     max_field_width = max(len("Field"), max(len(f) for f in fields))
     max_widths.append(max_field_width)

     # 后续列宽度（数据列）
     for i, entry in enumerate(dataList):
          col_values = [str(entry[field]) for field in fields]
          max_data_width = max(len(v) for v in col_values)
          header_width = len(f"Data{i+1}")
          max_widths.append(max(header_width, max_data_width))

     # 构建表格组件
     separator = "+" + "+".join("-" * (w + 2) for w in max_widths) + "+"
     header_row = "|" + "|".join(
     f" {header.center(max_widths[i])} " for i, header in enumerate(headers)) + "|"

     data_rows = []
     for row in rows:
          cells = []
          for i, value in enumerate(row):
               if i == 0:
                    # 字段列左对齐
                    aligned = value.ljust(max_widths[i])
               else:
                    # 数据列左对齐
                    aligned = value.ljust(max_widths[i])
               cells.append(f" {aligned} ")
          data_rows.append("|" + "|".join(cells) + "|")

     # 组合完整表格
     table = [separator, header_row, separator] + data_rows + [separator]
     table_str = "\n".join(table)
     return table_str


def save_red_data_to_csv(isDaLeTou,redDataList):
     str_date = datetime.now().strftime('%Y-%m-%d')
     if isDaLeTou:
          filename = f'./OutPut/DaLeTou_red_data_{str_date}.csv'
     else:
          filename = f'./OutPut/Ball_red_data_{str_date}.csv'
     with open(filename, 'a', newline='', encoding='utf-8') as output_file:
          writer = csv.writer(output_file)
          writer.writerow(redDataList)

def read_red_data_from_csv(filename):   
    with open(filename, 'r', newline='', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        return list(reader)


#分析索引
def AnalyseIndex(isDaLeTou,redData):
     print('分析索引')
     str_date = '2025-03-05'
     if isDaLeTou:
          fileName = f'./OutPut/DaLeTou_red_data_{str_date}.csv'
     else:
          fileName = f'./OutPut/Ball_red_data_{str_date}.csv'
     csv_data = read_red_data_from_csv(fileName)
     file = open(fileName, "a",encoding="utf-8")
     file.write(f'分析索引\n')
     totalTable = defaultdict(int)
     for row in csv_data:
          tt = []
          for strdata in row:
               data_dict = eval(strdata)
               index = data_dict['index']
               number = data_dict['number']
               count = data_dict['count']
               if number in redData:
                    totalTable[index] += 1
                    tt.append(index)
          if len(tt) > 0:
               print(f'index:{tt}')
               file.write(f'index:{tt}\n')
  
     totalTable = dict(sorted(totalTable.items(), key=lambda x: x[1], reverse=True))
     file.write(f'total:{totalTable}\n')            
     print("total:",totalTable)     
     file.close()

def Doit_100(isDaLeTou, ID, name, BallArray, BallDataList, recommendCount, loopTimes, redTopKeys, blueTopKeys, RMap, BMap, FixedMap,CheckMap):
    AllDataList = []
    for i in range(100):
          r, b = Doit(isDaLeTou, ID, name, BallArray, BallDataList, recommendCount, loopTimes, redTopKeys, blueTopKeys, RMap, BMap, FixedMap, CheckMap,False)
          dd = Selenium_Recommend_Analyse.DataList()
          dd.front = r
          dd.back = b
          AllDataList.append(dd)
          print(f'front:{r},back:{b}')
    db.SaveBall(AllDataList)


def enhanced_random(RandType,num):
    
    if  RandType == 1: 
          return random.randint(1, num)
    elif RandType == 2:
         return secrets.randbelow(num) + 1
'''
    # 用系统熵源初始化种子
    seed = secrets.randbits(64)
    random.seed(seed) 
    # 混合算法生成
    #浮点运算太消耗时间了
    return int(random.random() * secrets.randbelow(num))+1 
'''

def verify_model(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap,isPrint):
     times = 100
     AllDataList = []
     lastX = 5

     size = len(BallDataList)
     allMoney = 0
     for i in range(size - lastX, size):
          datalist = BallDataList[:-(size - i)]
          for t in range(times):
               r, b =  Doit(isHorse,isDaLeTou,ID,name,BallArray,datalist,recommendCount,loopTimes,redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap,isPrint)
               data = Selenium_Recommend_Analyse.DataList()
               data.front = []
               data.back = []
               data.front = r
               data.back = b
               AllDataList.append(data)
          balldata = BallDataList[i]

          if isinstance(balldata.blue, list):
               blue = balldata.blue
          else:
               blue = [balldata.blue]
          print(f'date:{balldata.date},i:{i},red:{balldata.red},blue:{blue}')
          money = Selenium_Recommend_Analyse.Doit(AllDataList,balldata.red,blue)
          print(f'money:{money}')
          allMoney += money
     print(f'allMoney:{allMoney}')

class ConfigData:
     def __init__(self):
          self.RMap = defaultdict(int)
          self.BMap = defaultdict(int)
          self.FixedMap = defaultdict(int)
          self.CheckMap = defaultdict(int)
          self.RandType = defaultdict(int)

#测试模型
def Test_model(ID,name,cfgData,AllDataMap,BallDataList,Array,isDaLeTou):
     
     legth = len(BallDataList)
     times = 100
     allM = 0
     for t in range(times):
        if t % 100 == 0:
          print(f'loop:{t+1}/{times}')
     
        for i in range(legth - 5, legth): 
            
            nextData = BallDataList[i]
            sliced_list = BallDataList[:i]
            redTopKeys,blueTopKeys = Analyse(sliced_list)  
            '''
            r,b=Doit(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,cfgData,False)
            DataList = []
            data = Selenium_Recommend_Analyse.DataList()
            data.front = r
            data.back = b
            DataList.append(data)        
            '''
            #DataList = DO_neer_comb(ID ,cfgData,BallDataList,redTopKeys,blueTopKeys,isDaLeTou,name,Array)
            DataList =DO_Easy_Comb(BallDataList,redTopKeys,blueTopKeys,isDaLeTou)

            m = Selenium_Recommend_Analyse.Doit(isDaLeTou,DataList,nextData.red,[nextData.blue])
            allM += m
     print(f'ID:{ID},times:{times},allM:{allM}')
            



cfgData = ConfigData()
RegID(cfgData)
isDaLeTou = False
BallDataList = []
AllDataMap = Selenium_Ball_Update.GetFileDate('2025-01-01')
for data in AllDataMap.values():
     BallDataList.append(data)
redTopKeys,blueTopKeys = Analyse(BallDataList)

def CallRun(): 
     recommendCount = 10000   #默认10000
     loopTimes = 1            #默认1
     isHorse = False
     name = f'./OutPut/Ball_Recommend_Log.txt'
     ID = 1001
     outRed,outBlue = Doit(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,cfgData,True)
     return outRed,outBlue

if __name__ == "__main__":
     #cfgData = ConfigData()
     #RegID(cfgData)
     now = datetime.now()
     random.seed(now.timestamp())

     CallRun()

     isDaLeTou = False
     BallDataList = []
     AllDataMap = Selenium_Ball_Update.GetFileDate('2025-01-01')
     for data in AllDataMap.values():
          BallDataList.append(data)
     redTopKeys,blueTopKeys = Analyse(BallDataList)

     recommendCount = 10000   #默认10000
     loopTimes = 1            #默认1
     isHorse = False

     PassRecommendCount = 1
     name = f'./OutPut/Ball_Recommend_Log.txt'
     ID = 1002
     #SelectRecommend(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap)
     ID = 1003
     #DO_neer_comb(ID,cfgData,BallDataList,redTopKeys,blueTopKeys,isDaLeTou,name,BallArray)

     
     #ID = 1001
     #Doit_100(isDaLeTou, ID, name, BallArray, BallDataList, recommendCount, loopTimes, redTopKeys, blueTopKeys, RMap, BMap, FixedMap,CheckMap)

     #allData = DoRecommendFiltration(isHorse,True,isDaLeTou,redTopKeys,blueTopKeys,1,BallDataList,True,True,BallArray,[])
     #for data in allData:
     #     print(f'front:{data.front},back:{data.back}')     

     #verify_model(isHorse,isDaLeTou,1002,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,RMap,BMap,FixedMap,CheckMap,False)


     ID = 1003
     #Doit(isHorse,isDaLeTou,ID,name,BallArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,cfgData,True)
     #DO_neer_comb(ID,cfgData,BallDataList,redTopKeys,blueTopKeys,isDaLeTou,name,BallArray)
     #Test_model(ID,name,cfgData,AllDataMap,BallDataList,BallArray,isDaLeTou)
     #DO_Easy_Comb(BallDataList,redTopKeys,blueTopKeys,isDaLeTou)
