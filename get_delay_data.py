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
from utils import readData


# 获取命令行参数
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


argv = get_argv()

checked_date = argv['time']
time_interval = ('09:30:00', '15:00:00')


def get_file_path(data_time, code, type, quote_source):
    type_map = {
        '1': 'MarketData',  # 三秒快照片
        '2': 'Order',  # 委托
        '3': 'Transaction',  # 成交
    }
    # tdf-wind,mdl-通联,tds-同花顺
    file_path = F'./data/{quote_source}/{data_time}/{type_map[type]}/{code}.csv'
    if os.path.exists(file_path) == False:
        print('不存在文件：', code)
        return
    return file_path


# 绘图 type: 1-MarketData,2-Order,3-Transaction
def pltStock(code, type, data_time, title_desc, quote_source):
    type_map = ['三秒快照', '逐笔委托', '逐笔成交']
    file_path = get_file_path(data_time, code, type, quote_source)
    df3 = readData(file_path, checked_date, time_interval)
    df3.to_csv('ddd3.csv')
    type = int(type) - 1

    # 下面都是绘图操作
    max_delay_time, how_long, max_rate = title_desc
    if (how_long == ''):
        title = F'{type_map[type]}数据延迟对比 股票代码：{code}，日期：{data_time}，最大延迟时间：{max_delay_time}，延迟峰值：{max_rate}'
    else:
        title = F'{type_map[type]}数据延迟对比 股票代码：{code}，日期：{data_time}，最大延迟时间：{max_delay_time}，延迟峰值：{max_rate}，延迟消化时间：{how_long}秒'
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title(title)
    x3 = pd.to_datetime(df3.x_axis)
    ax.plot(x3, df3.rate, color='y', label='同花顺')
    y = MultipleLocator(0.1)
    # ax.yaxis.set_major_locator(y) # 设置y轴刻度
    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter('%H:%M:%S'))  # 設置x軸主刻度顯示格式（日期）
    picPath = './pic/' + title + '.jpg'
    plt.savefig(picPath)
    plt.legend()
    plt.show()


# 消化时间数据处理和输出结果
def output_congestion_desc_result(data):
    max_row = (data[data['rate'] == data["rate"].max()]).reset_index()
    begin_delay = ((data[data['rate'] >= 1]).reset_index())
    min_rows = ((data[(data['rate'] < 1) & (
        data['timef'] > max_row['timef'][0])]).reset_index())
    max_delay_time = max_row['local_time']  # 最大延迟时间

    if (len(begin_delay) == 0):
        return (max_delay_time[0], '', max_row['rate'][0])
    if (len(min_rows) == 0):
        return (max_delay_time[0], '', max_row['rate'][0])
    else:
        begin_delay = begin_delay.iloc[0]
        min_row = (min_rows[min_rows['timef'] == min_rows["timef"].min()])
        how_long = min_row['time_s'][0] - begin_delay['time_s']
        return (max_delay_time[0], how_long, max_row['rate'][0])


# 获取消化时间
def congestion_desc(code, type, data_time, quote_source):
    file_path = get_file_path(data_time, code, type, quote_source)
    df = readData(file_path, checked_date, time_interval)
    df.to_csv(F'{quote_source}.csv')
    return output_congestion_desc_result(df)


if __name__ == '__main__':
    quote_source = 'tds'
    title_desc = congestion_desc(
        argv['code'], argv['type'], checked_date, quote_source)
    pltStock(argv['code'], argv['type'],
             argv['time'], title_desc, quote_source)
