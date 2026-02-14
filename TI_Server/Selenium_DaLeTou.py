import math

import random
from time import sleep
from datetime import datetime, timedelta
from collections import defaultdict
import Selenium_DaLeTou_Update
import Selenium_Ball 

from collections import defaultdict, OrderedDict
#import mysql_db as db


DaLeTouArray = [(1, 2, 2, 0), (2, 1, 2, 0), (2, 2, 1, 0), (0, 2, 2, 1), (3, 1, 0, 1), (1, 1, 2, 1), (1, 3, 1, 0), (2, 1, 1, 1),
(0, 1, 4, 0), (0, 1, 3, 1), (3, 0, 0, 2), (1, 1, 1, 2), (3, 1, 1, 0), (2, 0, 3, 0), (2, 0, 1, 2), (1, 0, 3, 1), 
(2, 1, 0, 2), (1, 1, 3, 0), (0, 2, 3, 0)]



def RegID(cfgData):
     cfgData.RMap[1001] = [20, 18, 3, 4, 5]
     cfgData.BMap[1001] = [2, 4]
     cfgData.FixedMap[1001] = False 
     cfgData.CheckMap[1001] = True 
     cfgData.RandType[1001] = 1

     #固定种子
     cfgData.RMap[1002] = [12, 3, 19, 25, 1]
     cfgData.BMap[1002] = [6, 5]
     cfgData.FixedMap[1002] = True
     cfgData.CheckMap[1002] = True 
     cfgData.RandType[1002] = 1

     cfgData.RMap[1004] = [20, 4, 18, 31, 16]
     cfgData.BMap[1004] = [5,3]
     cfgData.FixedMap[1004] = False
     cfgData.CheckMap[1004] = False 
     cfgData.RandType[1004] = 1

     cfgData.RMap[1005] = [20, 4, 18, 3, 31]
     cfgData.BMap[1005] = [5,3]
     cfgData.FixedMap[1005] = False
     cfgData.CheckMap[1005] = False 
     cfgData.RandType[1005] = 2



     #最新
     cfgData.RMap[1006] = [2,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19,17,18,20,21]
     cfgData.BMap[1006] = [2, 5]
     cfgData.FixedMap[1006] = False 
     cfgData.CheckMap[1006] = True 
     cfgData.RandType[1006] = 1
     

#排除法 
def DoPass():
     recommendCount = 10000
     red=[]
     blue = []
     rList = []
     bList = []
     for i in range(5):     
        r,b =  Selenium_Ball.Doit(isHorse,isDaLeTou,ID,name,DaLeTouArray,BallDataList,recommendCount,loopTimes,
               redTopKeys,blueTopKeys,cfgData,False)
        red += r
        blue += b
        rList.append(r)
        bList.append(b)
        sleep(5)
     red = list(set(red))
     blue = list(set(blue)) 

     recommendCount = 5
     AllDataList = Selenium_Ball.DoRecommend(isHorse,isDaLeTou, redTopKeys, blueTopKeys, recommendCount,
                                      [], False, False, DaLeTouArray, red)
     file = open(name, "a",encoding="utf-8") 
     current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
     file.write(f'------------DoPass------------\n')
     file.write(f'ID:{ID},date:{current_time_str}\n')
     file.write(f'Recommend\n')
     for r in rList:
          file.write(f'{r}\n')
     #过滤
     file.write(f'Filter\n')
     for info in AllDataList:
          r = info.front
          b = info.back
          recommend_red = list(set(r))
          print(f'{recommend_red} -- {b}')
          file.write(f'{recommend_red} -- {b}\n')
     file.write(f'----------------------------\n\n')
     file.close()


if __name__ == "__main__":


     cfgData = Selenium_Ball.ConfigData()
     RegID(cfgData)
     isDaLeTou = True
     BallDataList = []
     AllDataMap = Selenium_DaLeTou_Update.GetFileDate('2025-01-01')
     for data in AllDataMap.values():
          BallDataList.append(data)
     redTopKeys,blueTopKeys = Selenium_Ball.Analyse(BallDataList)

     recommendCount = 10000   #默认10000
     loopTimes = 1            #默认1
     isHorse = False
     name = f'./OutPut/DaLeTou_Recommend_Log.txt'

     
     #从推荐中选择
     ID = 1005
     #Selenium_Ball.SelectRecommend(isHorse,isDaLeTou,ID,name,DaLeTouArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,cfgData,True)

     #排除法
     ID = 1005
     #DoPass()

     ID = 1005
     Selenium_Ball.Doit(isHorse,isDaLeTou,ID,name,DaLeTouArray,BallDataList,recommendCount,loopTimes,redTopKeys,blueTopKeys,cfgData,True)
     #BigReward(redTopKeys,blueTopKeys)

     #Selenium_Ball.DO_neer_comb(ID,cfgData,BallDataList,redTopKeys,blueTopKeys,isDaLeTou,name,DaLeTouArray)

     #Selenium_Ball.DO_Easy_Comb(BallDataList,redTopKeys,blueTopKeys,isDaLeTou)
     #Selenium_Ball.Test_model(ID,name,cfgData,AllDataMap,BallDataList,DaLeTouArray,isDaLeTou)
