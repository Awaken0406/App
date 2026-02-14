
# 定义蓝色字体 ANSI 转义码
from collections import defaultdict
#import mysql_db as db

blue_color = "\033[34m"
# 恢复默认颜色 ANSI 转义码
reset_color = "\033[0m"
def Print_DaLeTou(AllDataList):
    one=two=three=four=five=six=seven=eight=nine = 0
    for data in AllDataList:
        if data.front_hit_count == 5 and data.back_hit_count == 2:        
            one += 1
            print('!!!one!!!',data.frontStr,data.backStr)
        elif data.front_hit_count == 5 and data.back_hit_count == 1:
            two += 1
            print('two',data.frontStr,data.backStr)
        elif data.front_hit_count == 5 and data.back_hit_count == 0:
            three += 1
            print('three',data.frontStr,data.backStr)
        elif (data.front_hit_count == 4 and data.back_hit_count == 2):
             four += 1
             print('four',data.frontStr,data.backStr)
        elif (data.front_hit_count == 4 and data.back_hit_count == 1):
             five += 1
             print('five',data.frontStr,data.backStr)
        elif data.front_hit_count == 3  and data.back_hit_count == 2:
             six += 1
             print('six',data.frontStr,data.backStr)
        elif (data.front_hit_count == 4 and data.back_hit_count == 0):
             seven += 1
             print('seven',data.frontStr,data.backStr)
        elif (data.front_hit_count == 3 and data.back_hit_count == 1) or (data.front_hit_count == 2 and data.back_hit_count == 2):
             eight += 1
             print('eight',data.frontStr,data.backStr)
        elif (data.front_hit_count == 3 and data.back_hit_count == 0) or (data.front_hit_count == 1 and data.back_hit_count == 2) or (data.front_hit_count == 2 and data.back_hit_count == 1) or (data.front_hit_count == 0 and data.back_hit_count == 2):
             nine += 1
             print('nine',data.frontStr,data.backStr)

    money = one*10000000 + two*100000 + three*10000 + four*3000 + five*300 + six*200 + seven*100 + eight*15 + nine*5
    #print(f'Total:{len(AllDataList)}')
    #print(f'{blue_color}One:{one},Two:{two},Three:{three},Four:{four},Five:{five},Six:{six},Seven:{seven},Eight:{eight},Nine:{nine}{reset_color}')
    #print(f'{blue_color}money:{money}{reset_color}')
    return money


def Print_Double(AllDataList):
    one=two=three=four=five=six=0
    for data in AllDataList:
        if data.front_hit_count == 6 and data.back_hit_count == 1:
            print('!!!one!!!',data.frontStr,data.backStr)
            one += 1
        elif data.front_hit_count == 6 and data.back_hit_count == 0:
            two += 1
            print('two',data.frontStr,data.backStr)
        elif data.front_hit_count == 5 and data.back_hit_count == 1:
            three += 1
            print('three',data.frontStr,data.backStr)
        elif (data.front_hit_count == 5 and data.back_hit_count == 0) or (data.front_hit_count == 4 and data.back_hit_count == 1):
             four += 1
             print('four',data.frontStr,data.backStr)
        elif (data.front_hit_count == 4 and data.back_hit_count == 0) or (data.front_hit_count == 3 and data.back_hit_count == 1):
             five += 1
             print('five',data.frontStr,data.backStr)
        elif (data.front_hit_count == 2 or data.front_hit_count == 1 or data.front_hit_count == 0) and data.back_hit_count == 1:
             six += 1
             print('six',data.frontStr,data.backStr)
    
    one1=two1=three1=four1=five1=six1=0
    for data in AllDataList:
        if data.front_hit_count == 6 and data.single_back_hit_count == 1:
            one1 += 1
        elif data.front_hit_count == 6 and data.single_back_hit_count == 0:
            two1 += 1
        elif data.front_hit_count == 5 and data.single_back_hit_count == 1:
            three1 += 1
        elif (data.front_hit_count == 5 and data.single_back_hit_count == 0) or (data.front_hit_count == 4 and data.single_back_hit_count == 1):
             four1 += 1
        elif (data.front_hit_count == 4 and data.single_back_hit_count == 0) or (data.front_hit_count == 3 and data.single_back_hit_count == 1):
             five1 += 1
        elif (data.front_hit_count == 2 or data.front_hit_count == 1 or data.front_hit_count == 0) and data.single_back_hit_count == 1:
             six1 += 1
    #print('DOUBLE:')
    money = one*6000000 + two*100000 + three*3000 + four*200 + five*10 + six*5   
    #print(f'{blue_color}One:{one},Two:{two},Three:{three},Four:{four},Five:{five},Six:{six}{reset_color}')
    #print(f'{blue_color}money:{money}{reset_color}')
    return money
'''
    print('SINGLE:')
    money1 = one1*6000000 + two1*100000 + three1*3000 + four1*200 + five1*10 + six1*5   
    print(f'{blue_color}One:{one1},Two:{two1},Three:{three1},Four:{four1},Five:{five1},Six:{six1}{reset_color}')
    print(f'{blue_color}money:{money1}{reset_color}')
'''


def LoadFile(fileName,AllDataList,find_front,find_back):
    g_Count = defaultdict(int)
    with open(fileName, 'r') as file:
        content = file.readlines()

    for line in content:
        if 'recommend' in line or line == '\n':
            continue
        parts = line.strip().split('--')       
        front_str, back_str = parts
        front_array = list(map(int, front_str.strip('[]').split(', ')))
        back_array = list(map(int, back_str.strip('[]').split(', ')))

        data = DataList()
        data.front = front_array
        data.back = back_array
        AllDataList.append(data)
    AnalyseFile(AllDataList,find_front,find_back)

def AnalyseFile(AllDataList,find_front,find_back):   
    for data in AllDataList:
        front_hit_count = 0
        back_hit_count = 0
        single_back_hit_count = 0
        frontStr = ''
        backStr = ''
        single_backStr = ''
        
        for num in  data.front:
            if num in find_front:
                front_hit_count += 1
                frontStr += blue_color + str(num) + reset_color
            else:  
                frontStr += str(num)
            frontStr +=  ' '
        
        for num in  data.back:
            if num in find_back:
                back_hit_count += 1
                backStr += blue_color + str(num) + reset_color 
            else:            
                backStr += str(num)
            backStr += ' '

        if data.back[0] == find_back[0]:
                single_back_hit_count += 1
                single_backStr += blue_color + str(num) + reset_color 
        else:            
                single_backStr += str(num)
        allHit = True
        for num in find_front:
            if num  not in data.front:
                allHit = False
        for num in find_back:
            if num not in data.back:
                allHit = False

        
        data.front_hit_count = front_hit_count
        data.back_hit_count = back_hit_count
        data.single_back_hit_count = single_back_hit_count
        data.frontStr = frontStr
        data.backStr = backStr
        data.single_backStr = single_backStr
        data.allHit = allHit

    #print(f'Total:{len(AllDataList)}')
''' for data in AllDataList:
        g_Count[data.front_hit_count + data.back_hit_count] += 1
        print(f'[{data.frontStr}]--[{data.backStr}], hitCount : {blue_color}{data.front_hit_count + data.back_hit_count}{reset_color}')

    for data in AllDataList:
        if data.allHit == True:
            print(f'All Hit :[{data.frontStr}]--[{data.backStr}]')

    g_Count = dict(sorted(g_Count.items(), key=lambda x: x[0]))    
    for k,v in g_Count.items():
        print(f'{blue_color}hit {k} ball has {v}{reset_color}')
''' 

class DataList:
        front = []
        back = []
        front_hit_count = 0
        back_hit_count = 0
        single_back_hit_count = 0
        frontStr=''
        backStr=''
        single_backStr = ''
        allHit = False


def Doit(isDaLeTou,AllDataList,find_front,find_back):
    AnalyseFile(AllDataList,find_front,find_back)
    if(isDaLeTou):
        return Print_DaLeTou(AllDataList)
    return Print_Double(AllDataList)
    

if __name__ == "__main__":
    AllDataList = db.LoadBableBall('Ball_2025_03_16')
    Doit(AllDataList,[4, 9, 14, 15, 18, 25],[15])
