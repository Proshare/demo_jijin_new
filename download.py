# 导入需要的模块
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family'] = 'sans-serif'
# 解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


# 抓取网页
def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


# 从网页抓取数据
def get_fund_data(code, per, sdate, edate, proxies=None):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {'type': 'lsjz', 'code': code, 'page': 1, 'per': per, 'sdate': sdate, 'edate': edate}
    html = get_url(url, params, proxies)

    soup = BeautifulSoup(html, 'html.parser')

    # 获取总页数
    pattern = re.compile(r'pages:(.*),')
    result = re.search(pattern, html).group(1)
    pages = int(result)

    # 获取表头
    heads = []
    for head in soup.findAll("th"):
        heads.append(head.contents[0])
    # 数据存取列表
    records = []
    # 从第1页开始抓取所有页面数据
    page = 1
    while page <= pages:
        params = {'type': 'lsjz', 'code': code, 'page': page, 'per': per, 'sdate': sdate, 'edate': edate}
        html = get_url(url, params, proxies)
        soup = BeautifulSoup(html, 'html.parser')
        # 获取数据
        for row in soup.findAll("tbody")[0].findAll("tr"):
            row_records = []
            for record in row.findAll('td'):
                val = record.contents
                # 处理空值
                if val == []:
                    row_records.append(np.nan)
                else:
                    row_records.append(val[0])
            # 记录数据
            records.append(row_records)
        # 下一页
        page = page + 1
    # 数据整理到dataframe
    np_records = np.array(records)

    data = pd.DataFrame()
    
    for col, col_name in enumerate(heads):
        data[col_name] = np_records[:, col]
    return data



names = ['华夏短债债券C', '嘉实中短债债券C', '富国信用债C', '财通资管鸿益中短债C', '国投瑞银恒泽中短债债券C', '招商双债增强债券E', '易方达高等级信用债债券C', '招商产业债C',
         '天弘弘泽短债债券C']
ids = ['004673', '006798', '000192', '006361', '006553', '003297', '000148', '001868', '007824']
# 主程序
import datetime

today = datetime.date.today()
oneday = datetime.timedelta(days=1)
yesterday = today - oneday

if __name__ == "__main__":
    for name, id in zip(names, ids):
        data = get_fund_data(id, per=1, sdate=yesterday, edate=today)
        # 修改数据类型
        data['净值日期'] = pd.to_datetime(data['净值日期'], format='%Y/%m/%d')
        data['单位净值'] = data['单位净值'].astype(float)
        data['累计净值'] = data['累计净值'].astype(float)
        data['日增长率'] = data['日增长率'].str.strip('%').astype(float)
        # 按照日期升序排序并重建索引
        data = data.sort_values(by='净值日期', axis=0, ascending=True).reset_index(drop=True)
        print('基金', name, today, '情况')
        print(data)


