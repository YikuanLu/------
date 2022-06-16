# coding:utf-8
import sys
import getopt
import datetime
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import time


# 读取数据
def readData(filePath):
    df = pandas.read_csv(filePath)
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


# 绘图
def pltStock(code, type):
    file1 = 'data\\' + code + '_TDF.csv'  # wind
    file2 = 'data\\' + code + '_MDL.csv'  # 通联
    file3 = 'data\\' + code + '_TDS.csv'  # 同花顺
    print('file3', file3)
    if os.path.exists(file1) == False or os.path.exists(file2) == False or os.path.exists(file3) == False:
        print('不存在文件：', code)
        return
    df1 = readData(file1)
    df2 = readData(file2)
    df3 = readData(file3)

    df1.to_csv("./TDF.csv", encoding="utf-8-sig",
               mode="a", header=True, index=False)
    df2.to_csv("./MDL.csv", encoding="utf-8-sig",
               mode="a", header=True, index=False)
    df3.to_csv("./TDS.csv", encoding="utf-8-sig",
               mode="a", header=True, index=False)

    x = []
    y = []
    for i, v in df1.iterrows():
        if pandas.isnull(v['avg']):
            continue

        timestr = time.strftime('%H%M', time.localtime(v['local_time']))
        # print(int(timestr))
        x.append(int(timestr))
        y.append(v['avg'])

    x2 = []
    y2 = []
    for i, v in df2.iterrows():
        if pandas.isnull(v['avg']):
            continue
        timestr = time.strftime('%H%M', time.localtime(v['local_time']))
        x2.append(int(timestr))
        y2.append(v['avg'])

    x3 = []
    y3 = []
    for i, v in df3.iterrows():
        if pandas.isnull(v['avg']):
            continue
        timestr = time.strftime('%H%M', time.localtime(v['local_time']))
        x3.append(int(timestr))
        y3.append(v['avg'])

    title = '整体延时-' + code + '-' + type
    plt.rcParams['font.sans-serif'] = ['SimHei']

    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H%M'))
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    plt.title(title)
    plt.plot(x, y, 'b', label='Wind')
    plt.plot(x2, y2, 'r', label='通联')
    plt.plot(x3, y3, 'y', label='同花顺')
    plt.legend()

    picPath = 'pic\\' + title + '.jpg'
    plt.savefig(picPath)
    plt.show()


# 测试逐笔成交延时
def testStockData():
    with open("底仓列表.txt", "r", encoding='utf-8') as f:
        code = f.readlines()[0]
        codeList = code.split(';')
        for data in codeList:
            symbol = data[0:6]
            if len(symbol) != 6:
                continue
            if symbol.startswith("0") == False and symbol.startswith("3") == False and symbol.startswith("6") == False:
                continue

            pltStock(symbol, 'O')


# 测试盘口快照延时
def testStockPrice():
    maxDelay = 0
    minDelay = 0
    with open("底仓列表.txt", "r", encoding='utf-8') as f:
        code = f.readlines()[0]
        codeList = code.split(';')
        for data in codeList:
            symbol = data[0:6]
            if len(symbol) != 6:
                continue
            # 深交所
            if symbol.startswith("0") == False and symbol.startswith("3") == False:
                continue
            # 上交所
            # if symbol.startswith("6") == False :
            #     continue

            file1 = '.\\data1\\' + symbol + '.csv'
            if os.path.exists(file1) == False:
                continue

            df1 = readData(file1)
            max = df1['avg'].max()
            min = df1['avg'].min()

            # 找出所有股票中，最大延时的股票
            if maxDelay < max:
                maxDelay = max
                print('max：', symbol)

            # print(df1)
            csvPath = 'csv\\' + symbol + '.csv'
            df1.to_csv(csvPath, encoding="utf-8-sig",
                       mode="a", header=True, index=False)
            #print(code, max, min)
            x = []
            y = []
            for i, v in df1.iterrows():
                if pandas.isnull(v['avg']):
                    continue
                timestr = time.strftime(
                    '%H%M', time.localtime(v['local_time']))
                x.append(int(timestr))
                y.append(v['avg'])

            title = '盘口快照-' + symbol
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.title(title)
            plt.plot(x, y, 'r')
            picPath = 'pic\\' + title + '.jpg'
            plt.savefig(picPath)
            plt.show()


if __name__ == '__main__':
    data = readData('./data/20220401/MarketData/000563.csv')
    # print(data)
    testStockData()
