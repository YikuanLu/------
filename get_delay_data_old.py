# coding:utf-8
import sys
import getopt
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from dateutil import parser
import matplotlib.dates as mdates  # 處理日期
from matplotlib.pyplot import MultipleLocator
import numpy as np
import datetime

checked_date = '20220610'
time_interval = ('09:30:00', '9:35:00')


# 获取有效时间区间
def get_effective_time():
    # 字符类型的时间
    datetime_struct = parser.parse(checked_date)
    today = datetime_struct.strftime('%Y-%m-%d ')
    start = F'{today} {time_interval[0]}'
    end = F'{today} {time_interval[1]}'
    start_timeArray = time.strptime(start, "%Y-%m-%d %H:%M:%S")
    end_timeArray = time.strptime(end, "%Y-%m-%d %H:%M:%S")
    # 转为时间戳
    start_timeStamp = time.mktime(start_timeArray)
    end_timeStamp = time.mktime(end_timeArray)
    return (start_timeStamp, end_timeStamp)


def time_to_ms_timestamp(x):
    millisecond = x.split('.')[1]
    time_str = str(int(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))))
    r = time_str+millisecond
    return float(r)


def time_to_s_timestamp(x):
    return float(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f')))


# 读取数据
def readData(filePath):
    raw_df = pd.read_csv(filePath)
    df = pd.DataFrame(raw_df, columns=['time', 'local_time'])

    # 给时间加上日期用于转时间戳
    datetime_struct = parser.parse(checked_date)
    today = datetime_struct.strftime('%Y-%m-%d ')
    df['x_axis'] = df['time']
    df['time'] = today + df['time']
    df['local_time'] = today + df['local_time']

    df['time_s'] = df['time'].apply(time_to_s_timestamp)
    df['timef'] = df['time'].apply(time_to_ms_timestamp)
    df['local_timef'] = df['local_time'].apply(time_to_ms_timestamp)

    start_timeStamp, end_timeStamp = get_effective_time()
    df = df.loc[(df.time_s >= start_timeStamp) & (
        df.time_s <= end_timeStamp)]

    df['rate'] = (df['local_timef'] - df['timef']) / 1000
    return df


def get_file_path(data_time, code, type):
    type_map = {
        '1': 'MarketData',  # 三秒快照片
        '2': 'Order',  # 委托
        '3': 'Transaction',  # 成交
    }
    file1 = F'./data/tdf/{data_time}/{type_map[type]}/{code}.csv'  # wind
    file2 = F'./data/mdl/{data_time}/{type_map[type]}/{code}.csv'  # 通联
    file3 = F'./data/tds/{data_time}/{type_map[type]}/{code}.csv'  # 同花顺
    return ('', '', file3)


# 绘图 type: 1-MarketData,2-Order,3-Transaction
def pltStock(code, type, data_time, title_desc):
    type_map = ['三秒快照', '逐笔委托', '逐笔成交']
    file1, file2, file3 = get_file_path(data_time, code, type)
    # if os.path.exists(file1) == False or os.path.exists(file2) == False or os.path.exists(file3) == False:
    #     print('不存在文件：', code)
    #     return
    # df1 = readData(file1)
    # df2 = readData(file2)
    df3 = readData(file3)
    # df1.to_csv('df1.csv')
    # df2.to_csv('df2.csv')
    # df3.to_csv('./out/df3.csv')
    type = int(type) - 1
    # 下面都是绘图操作
    max_delay_time, how_long, max_rate = title_desc
    if (how_long == ''):
        title = F'{type_map[type]}数据延迟对比 股票代码：{code}，日期：{data_time}，最大延迟时间：{max_delay_time}，延迟峰值：{max_rate}'
    else:
        title = F'{type_map[type]}数据延迟对比 股票代码：{code}，日期：{data_time}，最大延迟时间：{max_delay_time}，延迟峰值：{max_rate}，延迟消化时间：{how_long}秒'
    # my_y_ticks = np.arange(0, 10, 0.1)
    # plt.yticks(my_y_ticks)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title(title)
    # x1 = pd.to_datetime(df1.x_axis)
    # x2 = pd.to_datetime(df2.x_axis)
    x3 = pd.to_datetime(df3.x_axis)
    # ax.plot(x1, df1.rate, color='b', label='Wind')
    # ax.plot(x2, df2.rate, color='r', label='通联')
    ax.plot(x3, df3.rate, color='y', label='同花顺')
    y = MultipleLocator(0.1)
    # ax.yaxis.set_major_locator(y)
    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter('%H:%M:%S'))  # 設置x軸主刻度顯示格式（日期）
    picPath = './pic/' + title + '.jpg'
    plt.savefig(picPath)
    plt.legend()
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


# 消化时间数据处理和输出结果
def output_congestion_desc_result(data):
    max_row = (data[data['rate'] == data["rate"].max()]).reset_index()
    begin_delay = ((data[data['rate'] >= 1]).reset_index()).iloc[0]
    min_rows = ((data[(data['rate'] < 1) & (
        data['timef'] > max_row['timef'][0])]).reset_index())
    max_delay_time = max_row['time']  # 最大延迟时间
    if (len(min_rows) == 0):
        return (max_delay_time[0], '', max_row['rate'][0])
    else:
        min_row = (min_rows[min_rows['timef'] == min_rows["timef"].min()])
        how_long = min_row['time_s'][0] - begin_delay['time_s']
        return (max_delay_time[0], how_long, max_row['rate'][0])


# 获取消化时间
def congestion_desc(code, type, data_time):
    file1, file2, file3 = get_file_path(data_time, code, type)
    # if os.path.exists(file1) == False or os.path.exists(file2) == False or os.path.exists(file3) == False:
    #     print('不存在文件：', code)
    #     return
    # df1 = readData(file1)
    # df2 = readData(file2)
    df3 = readData(file3)
    # df1.to_csv('d1.csv')
    # df1.to_csv('d2.csv')
    df3.to_csv('d3.csv')
    return output_congestion_desc_result(df3)


if __name__ == '__main__':
    argv = get_argv()
    title_desc = congestion_desc(argv['code'], argv['type'], argv['time'])
    pltStock(argv['code'], argv['type'], argv['time'], title_desc)
