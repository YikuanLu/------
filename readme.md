## 获取万德，通联，同花顺数据延迟对比

1. 把三个通道的数据根据'mdl','tdf,'tds'命名文件夹后，放入data目录中，层级结构为<br/>
    data/<通道名>/<日期：20220407>/MarketData,Order,Transaction/<股票代码>.csv<br/>
2. 在项目根目录运行:python3 get_delay_data.py code=\<code> type=\<type> time=\<time><br/>
    type_map = {
        '1': 'MarketData',
        '2': 'Order',
        '3': 'Transaction',
    }<br/>
    ```ex: python3 get_delay_data.py code=000610 type=3 time=20220331```
3. 数据对比结果会生成jpg文件：F'{type_map[type]}数据延迟对比-股票代码：{code}，日期：{data_time}.jpg'存放于项目根目录下pic目录中

- MarketData - 三秒快照片
- Order - 委托
- Transaction - 成交