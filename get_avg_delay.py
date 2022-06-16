import sys
import getopt
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
import matplotlib.dates as mdates  # 處理日期
from dateutil import parser
from datetime import datetime
from brokenaxes import brokenaxes
import numpy as np

from utils import readData


checked_date = '20220615'
check_code = '002655'
time_interval = ('09:30:00', '14:55:00')

type_map = {
    '1': 'MarketData',  # 三秒快照片
    '2': 'Order',  # 委托
    '3': 'Transaction',  # 成交
}


# 获取单只票time_interval时间段内每分钟延迟的均值
def get_one_stock_date_range_avg(code):
    mdl_path = F'./data/tds/{checked_date}/{type_map["3"]}/{code}.csv'
    data = readData(mdl_path, checked_date, time_interval)
    # data.to_csv(F'./out/{code}_raw.csv')
    data.reset_index(inplace=True)
    # print(data)
    # data.to_csv('data.csv')
    datetime_struct = parser.parse(checked_date)
    today = datetime_struct.strftime('%Y-%m-%d ')
    start = F'{today} {time_interval[0]}'
    end = F'{today} {time_interval[1]}'

    # freq="T"，按分钟为间隔(频率)产生时间序列，等价于"min"
    date_range = pd.date_range(
        start=start, end=end, freq='T')
    date_range_df = pd.DataFrame(date_range, columns=['date'])
    date_range_df['timestamp'] = date_range_df['date'].apply(lambda x: (
        x - np.datetime64('1970-01-01T08:00:00')) / np.timedelta64(1, 'ms'))
    # date_range_df.to_csv('date_range_df.csv')
    # print(date_range_df)
    r_df = pd.DataFrame(columns=['code', 'x_axis', 'rate_avg'])

    for i in date_range_df.index:
        last_index = len(date_range)
        next_i = (i + 1) if (i + 1) < last_index else i
        if (i == next_i):
            break
        i_row = date_range_df.iloc[i]['timestamp']
        next_row = date_range_df.iloc[next_i]['timestamp']
        df = data[(data['local_timef'] > i_row) &
                  (data['local_timef'] <= next_row)]
        r_df = r_df.append(
            {'code': code, 'x_axis': date_range_df.iloc[i].date, 'rate_avg': df['rate'].mean()}, ignore_index=True)
    return r_df


# 归类交易所
def gp_type_szsh(gp):
    if int(gp[0:3]) >= 500:
        return 'sh'
    if int(gp[0:3]) <= 400:
        return 'sz'
    else:
        return 'else'


# 获取目录下所有文件
def get_all_file():
    path = F'./data/tds/{checked_date}/{type_map["3"]}'
    filenames = os.listdir(path)
    filenames = map(lambda x: x.split('.')[0], filenames)
    return list(filenames)


# 生成均值
def get_avg(stock_list):
    df = pd.DataFrame()
    for i, v in enumerate(stock_list):
        check_data = get_one_stock_date_range_avg(v)
        df = pd.concat([df, check_data])
        print(F'生成{v}数据中...')
    df = df.dropna()
    # return df

    group_obj = df.groupby('x_axis')
    result_df = pd.DataFrame(columns=['time', 'rate_avg'])
    for name, item in group_obj:
        result_df = result_df.append(
            {'time': name, 'rate_avg': item['rate_avg'].mean()}, ignore_index=True)
    result_df.sort_values(by='time', inplace=True)
    result_df.to_csv('./out/sh_avg.csv')
    return result_df


if __name__ == '__main__':
    filenames = get_all_file()
    sh_ls = []
    sz_ls = []
    el_ls = []
    for i, v in enumerate(filenames):
        stock_type = gp_type_szsh(v)
        if (stock_type == 'sh'):
            sh_ls.append(v)
        elif (stock_type == 'sz'):
            sz_ls.append(v)
        else:
            el_ls.append(v)

    sh_data = get_avg(sh_ls[0:4])
    sh_data.to_csv('./out/sh_data.csv')
    # sz_data = get_avg(sz_ls[0:4])

    bax = brokenaxes(xlims=((datetime(2022, 6, 15, 9, 00, 00), datetime(
        2022, 6, 15, 11, 30, 00)), (datetime(2022, 6, 15, 13, 00, 00), datetime(2022, 6, 15, 15, 00, 00))))

    title = '整体平均延迟'
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # fig = plt.figure()
    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter('%H:%M:%S'))  # 設置x軸主刻度顯示格式（日期）
    # ax = fig.add_subplot(1, 1, 1)
    plt.title(title)
    x = sh_data['time']
    y = sh_data['rate_avg']
    bax.plot(x, y)
    plt.show()
