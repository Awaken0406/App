import sys
import pymysql
from  datetime import date
import Selenium_Recommend_Analyse

import datetime



db = pymysql.connect(host='192.168.3.21',user='root',password='123456',port=3306,database='senge')
if db.ping() == False:
    print("connect database fail")
    sys.exit()
print("Connect database suc")
cursor = db.cursor()




#time_date = datetime.datetime.strptime('2023-5-10', "%Y-%m-%d").date()

def DoSql(sql):
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        db.rollback()
        print("error",e)

def SaveBall(AllDataList):
    tableName = 'Ball_' + datetime.datetime.now().strftime("%Y_%m_%d")  
    create_sql = f'CREATE TABLE IF NOT EXISTS {tableName} (red VARCHAR(255),blue VARCHAR(255),time VARCHAR(255));'
    DoSql(create_sql)

    sec_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for d in AllDataList:
        front =  ', '.join(str(num) for num in d.front)
        back = ', '.join(str(num) for num in d.back)
        sql= f'INSERT INTO {tableName} (red,blue,time) values("{front}","{back}","{sec_str}");'
        DoSql(sql)

def LoadBableBall(tableName):
   query = f"SELECT * FROM {tableName}"
   cursor.execute(query)
   AllDataList = []

   # 遍历查询结果
 
   for row in cursor.fetchall():
        data = Selenium_Recommend_Analyse.DataList()
        data.front = []
        data.back = []
        numbers_list1 = row[0].split(', ')
        numbers_list2 = row[1].split(', ')
        data.front = [int(num) for num in numbers_list1]
        data.back = [int(num) for num in numbers_list2]
        AllDataList.append(data)
   return AllDataList
 