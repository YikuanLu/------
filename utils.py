import time
from dateutil import parser
import pandas as pd


# 时间转毫秒时间戳
def time_to_ms_timestamp(x):
    millisecond = x.split('.')[1]
    time_str = str(int(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))))
    r = time_str+millisecond
    return float(r)


# 时间转秒时间戳
def time_to_s_timestamp(x):
    return float(time.mktime(time.strptime(x, '%Y-%m-%d %H:%M:%S.%f')))


# 获取有效时间区间
def get_effective_time(time_interval, checked_date):
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


# 读取数据
def readData(filePath, check_date, period):
    raw_df = pd.read_csv(filePath)
    df = pd.DataFrame(raw_df, columns=['time', 'local_time'])
    # 给时间加上日期用于转时间戳
    datetime_struct = parser.parse(check_date)
    today = datetime_struct.strftime('%Y-%m-%d ')
    df['x_axis'] = df['time']
    df['time'] = today + df['time']
    df['local_time'] = today + df['local_time']

    df['time_s'] = df['time'].apply(time_to_s_timestamp)
    df['timef'] = df['time'].apply(time_to_ms_timestamp)
    df['local_timef'] = df['local_time'].apply(time_to_ms_timestamp)

    start_timeStamp, end_timeStamp = get_effective_time(
        period, check_date)
    df = df.loc[(df.time_s >= start_timeStamp) & (
        df.time_s <= end_timeStamp)]

    df['rate'] = (df['local_timef'] - df['timef']) / 1000
    return df
