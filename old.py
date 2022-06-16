# coding:utf-8
import sys
import getopt
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import time


# 读取数据
def readData(filePath):
    df = pd.read_csv(filePath)
    df['timeF'] = df['time']
    df['local_timeF'] = df['local_time']

    today = time.strftime("%Y-%m-%d ")
    df['time'] = today + df['time']
    df['local_time'] = today + df['local_time']
    df['local_time'] = df['local_time'].apply(
        lambda x: time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f')))
    df['time'] = df['time'].apply(lambda x: time.mktime(
        time.strptime(x, '%Y-%m-%d %H:%M:%S.%f')))

    df['rate'] = df['local_time'] - df['time']

    df_new = df[df['rate'] <= 500].copy()  # 过滤无效数据, wind会发送昨日的数据
    df_new['sum'] = df_new['rate'].cumsum()

    avg = []
    index = 1
    for i, v in df_new.iterrows():
        avg.append(v['sum']/index)
        index = index + 1

    df_new['avg'] = avg
    return df_new


# 绘图 type: 1-MarketData,2-Order,3-Transaction
def pltStock(code, type, data_time):
    type_map = {
        '1': 'MarketData',
        '2': 'Order',
        '3': 'Transaction',
    }

    file1 = F'./data/tdf/{data_time}/{type_map[type]}/{code}.csv'  # wind
    file2 = F'./data/mdl/{data_time}/{type_map[type]}/{code}.csv'  # 通联
    file3 = F'./data/tds/{data_time}/{type_map[type]}/{code}.csv'  # 同花顺

    if os.path.exists(file1) == False or os.path.exists(file2) == False or os.path.exists(file3) == False:
        print('不存在文件：', code)
        return
    df1 = readData(file1)
    df2 = readData(file2)
    df3 = readData(file3)
    
    x1 = df1['local_time'].apply(lambda x: time.localtime(x))
    # x1 = x1.apply(lambda x: time.strftime("%H:%M:%S", x))
    x1 = x1.apply(lambda x: int(time.strftime("%H%M%S", x)))
    y1 = df1['avg']

    x2 = df2['local_time'].apply(lambda x: time.localtime(x))
    # x2 = x2.apply(lambda x: time.strftime("%H:%M:%S", x))
    x2 = x2.apply(lambda x: int(time.strftime("%H%M%S", x)))
    y2 = df2['avg']

    x3 = df3['local_time'].apply(lambda x: time.localtime(x))
    # x3 = x3.apply(lambda x: time.strftime("%H:%M:%S", x))
    x3 = x3.apply(lambda x: int(time.strftime("%H%M%S", x)))
    y3 = df3['avg']

    # title = '整体延时-' + code + '-' + type
    title = F'{type_map[type]}数据延迟对比-股票代码：{code}，日期：{data_time}'
    plt.rcParams['font.sans-serif'] = ['SimHei']

    # 横坐标日期范围及间隔
    # plt.xticks(pd.date_range(start='2022-03-31 00:00:00', periods=10, freq='ms'))
    # plt.xticks(range(0,len(x1),600)) #共365个值，每20个点显示一次

    plt.title(title)
    plt.plot(x1, y1, 'b', label='Wind')
    plt.plot(x2, y2, 'r', label='通联')
    plt.plot(x3, y3, 'y', label='同花顺')
    plt.legend()

    picPath = './pic/' + title + '.jpg'
    plt.savefig(picPath)
    
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    
    plt.show()


def get_argv():
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('market_view.py code=<stock_code> type=<type<1|2|3>> time=<ex:20220407>')
        sys.exit(2)
    art_ma = {}
    for arg in args:
        key = arg.split('=')[0]
        value = arg.split('=')[1]
        art_ma[key] = value
    return art_ma


if __name__ == '__main__':
    argv = get_argv()
    pltStock(argv['code'], argv['type'], argv['time'])
