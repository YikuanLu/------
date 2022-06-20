## 可视化行情延迟数据

1. 把三个通道的数据根据'mdl','tdf,'tds'命名文件夹后，放入data目录中，层级结构为<br/>
    data/<通道名>/<日期：20220407>/MarketData,Order,Transaction/<股票代码>.csv<br/>
2. 在项目根目录运行:python3 get_delay_data.py code=\<code> type=\<type> time=\<time><br/>
    type_map = {
        '1': 'MarketData', # 三秒快照片
        '2': 'Order', # 逐笔委托
        '3': 'Transaction', 逐笔成交
    }<br/>
    ```ex: python3 get_delay_data.py code=000610 type=3 time=20220331```
3. 数据对比结果会生成jpg文件：F'{type_map[type]}数据延迟对比-股票代码：{code}，日期：{data_time}.jpg'存放于项目根目录下pic目录中

4. 对比全市场延迟数据，运行get_avg_delay.py文件