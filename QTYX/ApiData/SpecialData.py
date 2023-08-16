#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究
import pandas as pd
import os
import requests
import random
import json
import re
import numpy as np
import time
import urllib3
import pywencai as wc

from urllib import request
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from CommIf.SqliteHandle import DataBase_Sqlite
from ApiData.Tushare import basic_code_list

urllib3.disable_warnings()
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 200)  # 最多显示数据的行数
pd.set_option('display.max_columns', 15) # 显示的最大列数

# 爬虫特色数据后端
class DataBackend():

    store_path = '' # 在子类中定义
    file_name = '' # 在子类中定义

    def __init__(self):
        self.df_total = pd.DataFrame()  # 新建一个空的DataFrame 存储处理后的特色数据
        #self.cur_time = self.get_latest_trade_dates # 初始化当前时间

    @property
    def get_latest_trade_dates(self):
        # 获取最近一个交易日期
        return datetime.now().strftime("%Y%m%d")  # 初始化值

    def save_db(self, store_path, file_name, cur_time):

        file_exist = Path(store_path + u'stock-daily.db')
        operate_sqlite = DataBase_Sqlite(file_exist)
        operate_sqlite.save_table(self.df_total, f'{0}-{1}'.format(file_name, cur_time))

    def save_csv(self, store_path, file_name, cur_time):

        file_exist = Path(store_path + u"{0}-{1}.csv".format(file_name, cur_time))
        self.df_total.to_csv(file_exist, columns=self.df_total.columns, index=True, encoding='GBK')

    def start_run(self, trade_date):
        '''
        DataBackend 是一个抽象类，必须实现这个方法
        :param:
        :return:
        '''
        raise NotImplementedError

    def datafame_join(self, date_val):

        file_exist = Path(self.store_path + u"{0}-{1}.csv".format(self.file_name, date_val))

        if file_exist.is_file() == False:
            self.syslog.re_print(f"开始获取A股{self.file_name}...\n")
            try:
                self.df_total = self.start_run(date_val)
                self.save_csv(self.store_path, self.file_name, date_val)
            except:
                self.syslog.re_print(f"获取{self.file_name}出错！检查数据接口是否有效！\n")
                self.df_total = pd.DataFrame()

        else:
            self.syslog.re_print("历史数据已经存在...\n")
            try:
                self.df_total = pd.read_csv(self.store_path + u"{0}-{1}.csv".format(self.file_name, date_val), parse_dates=True, index_col=0, encoding='GBK') # utf-8-sig
            except:
                self.syslog.re_print("请检查历史数据中该文件是否正常！\n")
                self.df_total = pd.DataFrame()

        if self.df_total.empty != True:
            self.syslog.re_print(f"A股{self.file_name}获取成功！\n")
            return self.df_total
        else:
            return pd.DataFrame()

    @staticmethod
    def fuzzy_finder(key, data):
        """
        模糊查找器
        :param key: 关键字
        :param data: 数据
        :return: list
        """
        # 结果列表
        suggestions = []
        # 非贪婪匹配，转换 'djm' 为 'd.*?j.*?m'
        # pattern = '.*?'.join(key)
        pattern = '.*%s.*' % (key)
        regex = re.compile(pattern)
        for item in data:
            match = regex.search(item)
            if match:
                suggestions.append(item)
        return suggestions


class NorthMoneyImp(DataBackend):

    store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/NorthData/'
    file_name = "每日北向资金持仓"

    def __init__(self, syslog_obj):
        DataBackend.__init__(self)
        self.syslog = syslog_obj

    def backup_run(self, start_date: str = "20211027", end_date: str = "20211027"):
        """
        东方财富网-数据中心-北向资金-每日个股统计
        http://data.eastmoney.com/hsgtcg/StockStatistics.aspx
        :param start_date: 指定数据获取开始的时间, e.g., "20200713"
        :type start_date: str
        :param end_date: 指定数据获取结束的时间, e.g., "20200715"
        :type end_date:str
        :return: 指定市场和指定时间段的每日个股统计数据
        :rtype: pandas.DataFrame
        """
        start_date = "-".join([start_date[:4], start_date[4:6], start_date[6:]])
        end_date = "-".join([end_date[:4], end_date[4:6], end_date[6:]])

        params = {
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
            "pageSize": "1000",
            "pageNumber": "1",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": f"""(INTERVAL_TYPE="1")(MUTUAL_TYPE in ("001","003"))(TRADE_DATE>='{start_date}')(TRADE_DATE<='{end_date}')""",
            "rt": "53160469",
            "reportName": "RPT_MUTUAL_STOCK_NORTHSTA",
        }
        if start_date == end_date:
            params.update(
                {
                    "filter": f"""(INTERVAL_TYPE="1")(MUTUAL_TYPE in ("001","003"))(TRADE_DATE='{start_date}')"""
                }
            )
        url = "http://datacenter-web.eastmoney.com/api/data/v1/get"
        r = requests.get(url, params=params)
        data_json = r.json()
        total_page = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, int(total_page) + 1):
            params.update({"pageNumber": page})
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)

        big_df.columns = [
            "-",
            "-",
            "持股日期",
            "-",
            "股票名称",
            "-",
            "-",
            "股票代码",
            "-",
            "-",
            "-",
            "-",
            "持股数量",
            "持股市值",
            "-",
            "持股数量占发行股百分比",
            "当日收盘价",
            "当日涨跌幅",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "持股市值变化-1日",
            "持股市值变化-5日",
            "持股市值变化-10日",
            "-",
            "-",
        ]
        big_df = big_df[
            [
                "持股日期",
                "股票代码",
                "股票名称",
                "当日收盘价",
                "当日涨跌幅",
                "持股数量",
                "持股市值",
                "持股数量占发行股百分比",
                "持股市值变化-1日",
                "持股市值变化-5日",
                "持股市值变化-10日",
            ]
        ]
        big_df["股票代码"] = big_df["股票代码"].apply(lambda x: x+'.SH' if x[0]=='6' else x+'.SZ')

        big_df["持股日期"] = pd.to_datetime(big_df["持股日期"]).dt.date
        big_df["当日收盘价"] = pd.to_numeric(big_df["当日收盘价"])
        big_df["当日涨跌幅"] = pd.to_numeric(big_df["当日涨跌幅"])
        big_df["持股数量"] = pd.to_numeric(big_df["持股数量"])
        big_df["持股市值"] = pd.to_numeric(big_df["持股市值"])
        big_df["持股数量占发行股百分比"] = pd.to_numeric(big_df["持股数量占发行股百分比"])
        big_df["持股市值变化-1日"] = pd.to_numeric(big_df["持股市值变化-1日"])
        big_df["持股市值变化-5日"] = pd.to_numeric(big_df["持股市值变化-5日"])
        big_df["持股市值变化-10日"] = pd.to_numeric(big_df["持股市值变化-10日"])
        return big_df

    def start_run(self, trade_date="") -> pd.DataFrame:
        """
        东方财富-数据中心-沪深港通持股-个股排行
        http://data.eastmoney.com/hsgtcg/list.html
        :param market: choice of {"北向", "沪股通", "深股通"}
        :type market: str
        :param indicator: choice of {"今日排行", "3日排行", "5日排行", "10日排行", "月排行", "季排行", "年排行"}
        :type indicator: str
        :return: 指定 sector 和 indicator 的数据
        :rtype: pandas.DataFrame
        """
        market = "北向"
        indicator = "今日排行"
        url = "http://data.eastmoney.com/hsgtcg/list.html"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        date = (
            soup.find("div", attrs={"class": "title"})
                .find("span")
                .text.strip("（")
                .strip("）")
        )
        url = "http://datacenter-web.eastmoney.com/api/data/v1/get"
        if indicator == "今日排行":
            indicator_type = "1"
        if indicator == "3日排行":
            indicator_type = "3"
        if indicator == "5日排行":
            indicator_type = "5"
        if indicator == "10日排行":
            indicator_type = "10"
        if indicator == "月排行":
            indicator_type = "M"
        if indicator == "季排行":
            indicator_type = "Q"
        if indicator == "年排行":
            indicator_type = "Y"
        if market == "北向":
            filter_str = (
                f"""(TRADE_DATE='{date}')(INTERVAL_TYPE="{indicator_type}")"""
            )
        elif market == "沪股通":
            filter_str = f"""(TRADE_DATE='{date}')(INTERVAL_TYPE="{indicator_type}")(MUTUAL_TYPE="001")"""
        elif market == "深股通":
            filter_str = f"""(TRADE_DATE='{date}')(INTERVAL_TYPE="{indicator_type}")(MUTUAL_TYPE="003")"""
        params = {
            "sortColumns": "ADD_MARKET_CAP",
            "sortTypes": "-1",
            "pageSize": "50000",
            "pageNumber": "1",
            "reportName": "RPT_MUTUAL_STOCK_NORTHSTA",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "filter": filter_str,
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        page_num = data_json["result"]["pages"]
        big_df = pd.DataFrame()
        for page in range(1, page_num + 1):
            params.update({"pageNumber": page})
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["result"]["data"])
            big_df = pd.concat([big_df, temp_df], ignore_index=True)

        big_df.reset_index(inplace=True)
        big_df["index"] = range(1, len(big_df) + 1)
        big_df.columns = [
            "序号",
            "_",
            "_",
            "日期",
            "_",
            "股票名称",
            "_",
            "_",
            "股票代码",
            "_",
            "_",
            "_",
            "_",
            "今持-股数(万)",
            "今持-市值(万)",
            "今持-占流通股比",
            "今持-占总股本比",
            "今收盘价",
            "今涨跌幅",
            "_",
            "所属板块",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            f'{indicator.split("排")[0]}增持-市值(万)',
            f'{indicator.split("排")[0]}增持-股数(万)',
            f'{indicator.split("排")[0]}增持-市值增幅',
            f'{indicator.split("排")[0]}增持-占流通股比',
            f'{indicator.split("排")[0]}增持-占总股本比',
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
            "_",
        ]
        big_df = big_df[
            [
                "股票代码",
                "股票名称",
                "今收盘价",
                "今涨跌幅",
                "今持-股数(万)",
                "今持-市值(万)",
                "今持-占流通股比",
                "今持-占总股本比",
                f'{indicator.split("排")[0]}增持-股数(万)',
                f'{indicator.split("排")[0]}增持-市值(万)',
                f'{indicator.split("排")[0]}增持-市值增幅',
                f'{indicator.split("排")[0]}增持-占流通股比',
                f'{indicator.split("排")[0]}增持-占总股本比',
                "所属板块",
                "日期",
            ]
        ]
        big_df["股票代码"] = big_df["股票代码"].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
        big_df["今收盘价"] = pd.to_numeric(big_df["今收盘价"])
        big_df["今涨跌幅"] = pd.to_numeric(big_df["今涨跌幅"])
        big_df["今持-股数(万)"] = pd.to_numeric(big_df["今持-股数(万)"])
        big_df["今持-市值(万)"] = pd.to_numeric(big_df["今持-市值(万)"])
        big_df["今持-占流通股比"] = pd.to_numeric(big_df["今持-占流通股比"])
        big_df["今持-占总股本比"] = pd.to_numeric(big_df["今持-占总股本比"])
        big_df[f'{indicator.split("排")[0]}增持-股数(万)'] = pd.to_numeric(
            big_df[f'{indicator.split("排")[0]}增持-股数(万)']
        )
        big_df[f'{indicator.split("排")[0]}增持-市值(万)'] = pd.to_numeric(
            big_df[f'{indicator.split("排")[0]}增持-市值(万)']
        )
        big_df[f'{indicator.split("排")[0]}增持-市值增幅'] = pd.to_numeric(
            big_df[f'{indicator.split("排")[0]}增持-市值增幅']
        )
        big_df[f'{indicator.split("排")[0]}增持-占流通股比'] = pd.to_numeric(
            big_df[f'{indicator.split("排")[0]}增持-占流通股比']
        )
        big_df[f'{indicator.split("排")[0]}增持-占总股本比'] = pd.to_numeric(
            big_df[f'{indicator.split("排")[0]}增持-占总股本比']
        )
        big_df["日期"] = pd.to_datetime(big_df["日期"]).dt.date

        return big_df

class DailyIndImp(DataBackend):

    store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/DailyData/'
    file_name = "每日基本指标"
    pages = 12 # 目前A股的股票数量需要12页

    def __init__(self, syslog_obj):
        DataBackend.__init__(self)
        self.syslog = syslog_obj

    def get_header(self):

        # 构造请求头信息,随机抽取信息
        agent1 = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
        agent2 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'
        agent3 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
        agent4 = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) '
        agent5 = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) '

        agent = random.choice([agent1, agent2, agent3, agent4, agent5])  # 请求头信息

        header = {
            'User-Agent': agent
        }
        return header

    def start_run(self, trade_date=""):

        df_basic = pd.DataFrame()  # 新建一个空的DataFrame
        for page in range(1, self.pages):

            url = "http://75.push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124006808348016960819_1607923077127" \
                  "&pn=" + str(
                page) + "&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23" \
                        "&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f23&_=1607923077268"

            req_obj = request.Request(url, headers=self.get_header())
            resp = request.urlopen(req_obj).read().decode(encoding='utf-8')

            pattern = re.compile(r'"diff":\[(.*?)\]', re.S).findall(resp)
            st_data = pattern[0].replace("},{", "}walt{").split('walt')
            stocks = []

            for i in range(len(st_data)):

                stock = json.loads(st_data[i])
                stock_all = str(stock['f12']) + "," + str(stock['f14']) + "," + str(stock['f2']) + "," + str(
                    stock['f4']) + "," + \
                            str(stock['f3']) + "," + str(stock['f5']) + "," + str(stock['f6']) + "," + str(
                    stock['f7']) + "," + \
                            str(stock['f15']) + "," + str(stock['f16']) + "," + str(stock['f17']) + "," + str(
                    stock['f18']) + "," + \
                            str(stock['f10']) + "," + str(stock['f8']) + "," + str(stock['f9']) + "," + str(
                    stock['f23']) + "," + \
                            str(stock['f20']) + "," + str(stock['f21'])

                stocks.append(stock_all.split(","))

            df = pd.DataFrame(stocks, dtype=object)

            columns = {0: "股票代码", 1: "股票名称", 2: "最新价格", 3: "涨跌额", 4: "涨跌幅", 5: "成交量", 6: "成交额", 7: "振幅", 8: "最高", 9: "最低",
                       10: "今开", 11: "昨收", 12: "量比", 13: "换手率", 14: "市盈率(动态)", 15: "市净率", 16: "总市值", 17: "流通市值"}
            df.rename(columns=columns, inplace=True)

            df_basic = pd.concat([df_basic, df], ignore_index=True)

            time.sleep(0.5)

        df_basic.replace("-", np.nan, inplace=True)

        df_basic = df_basic.astype({'最新价格': 'float64', '涨跌额': 'float64', '涨跌幅': 'float64',
                                              '成交量': 'float64', '成交额': 'float64', '振幅': 'float64',
                                              '最高': 'float64', '最低': 'float64', '今开': 'float64', '昨收': 'float64',
                                              '量比': 'float64', '换手率': 'float64', '市盈率(动态)': 'float64', '市净率': 'float64',
                                              '总市值': 'float64', '流通市值': 'float64'})

        df_basic["股票代码"] = df_basic["股票代码"].apply(lambda x: x+'.SH' if x[0]=='6' else x+'.SZ')

        df_basic["成交额(万)"] = np.round(df_basic["成交额"]/10000, 2)
        df_basic["总市值(万)"] = np.round(df_basic["总市值"]/10000, 2)
        df_basic["流通市值(万)"] = np.round(df_basic["流通市值"]/10000, 2)
        df_basic = df_basic.drop(['成交额', '总市值', '流通市值'], axis=1)

        try:
            df_extbasic = basic_code_list(['ts_code','symbol','name','area','industry','list_date'])
            df_extbasic.rename(columns={"ts_code": "股票代码", "area": "所在地域", "industry": u"所属行业","list_date": u"上市日期"},
                              inplace=True)
        except:
            self.syslog.re_print("请检查tushare接口-[stock_basic]是否正常！\n")
            df_extbasic = pd.DataFrame()

        if (df_extbasic.empty != True) and (df_basic.empty != True): # 两个接口都正常是合并

            df_basic = pd.merge(df_basic, df_extbasic, on='股票代码', left_index=False, right_index=False,
                         how='inner')
            df_basic.drop(['symbol', 'name'], axis=1, inplace=True)

        return df_basic

class UpLimitImp(DataBackend):

    store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/UplimData/'
    file_name = "每日涨停个股明细"

    def __init__(self, syslog_obj):
        DataBackend.__init__(self)
        self.syslog = syslog_obj

    def get_wencai_data(self, word='涨停', total_page=1):
        '''
        获取问财数据
        :return:
        '''
        result = pd.DataFrame()
        try:
            df = wc.get(question=word, loop=total_page)
            # 如果没有数据推出
            if df.shape[0] > 0:
                df = df[df.columns[:-2]]
                result = pd.concat([result, df], ignore_index=True)
            else:
                print('数据获取完成')
        except:
            pass

        result.rename(columns={"股票简称": "股票名称"}, inplace=True)

        if "涨停" in word:
            old_columns = self.fuzzy_finder("涨停原因类别",
                                            result.columns.to_list())[0]
            result.rename(columns={old_columns: "涨停原因类别"}, inplace=True)
            result = result.loc[:, ['股票名称', '涨停原因类别']]  # 返回指定范围内的数据
            result["股票名称"] = result["股票名称"].apply(lambda x: x.replace(" ", ""))

        return result

    def get_header(self):

        # 构造请求头信息,随机抽取信息
        agent1 = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
        agent2 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'
        agent3 = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
        agent4 = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) '
        agent5 = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR ' \
                 '3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) '

        agent = random.choice([agent1, agent2, agent3, agent4, agent5])  # 请求头信息

        header = {
            'User-Agent': agent,
            'Referer': 'https://www.eastmoney.com/'
        }
        return header

    # 炸板次数打分（0-10）
    def cal_zbc(self, y):
        '''y是炸板次数'''
        try:
            return max(10 - y, 0)
        except:
            return 0

    # 连板天数打分（0-10）
    def cal_lbc(self, y):
        '''y是连板天数'''
        try:
            return 5 + min(y, 5) if y <= 5 else 5 - min(round(y - 5), 5)
        except:
            return 0

    # 封成比打分（0-10）
    def cal_fcb(self, y):
        '''y是封成比'''
        try:
            return min(int(y), 10)
        except:
            return 0

    # 最终封板时间打分（0-10）
    def cal_lbt(self, y):
        '''y是最终封板时间'''
        try:
            return 10 - (int(y.split(":")[0]) - 9) / (14 - 9) * 10
        except:
            return 0

    def start_run(self, trade_date=""):

        try:
            url = 'http://push2ex.eastmoney.com/getTopicZTPool?cb=callbackdata4570496&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=1000&sort=fbt:asc&date=' + str(
                trade_date) + "&_=1644837745766"

            req_obj = request.Request(url, headers=self.get_header())
            resp = request.urlopen(req_obj).read().decode(encoding='utf-8')
            pattern = re.compile(r'"pool":\[(.*?)\]', re.S).findall(resp)

            st_data = pattern[0].replace("},{", "}walt{").split('walt')

            stocks = []

            for i in range(len(st_data)):
                # stock = st_data[i].replace('"',"").split(",")
                stock = json.loads(st_data[i])
                fenzi = str(stock['zttj']['ct'])
                fenmu = str(stock['zttj']['days'])
                # print(len(str(stock['fbt'])))

                stock_all = str(stock['c']) + "," + str(stock['n']) + "," + str(stock['p'] / 1000) + "," + \
                            str(round((stock['zdp']), 2)) + "," + str(round(stock['amount'] / 100000000, 2)) + "," + \
                            str(round(stock['ltsz'] / 100000000, 2)) + "," + \
                            str(str(round(stock['hs'], 2))) + "," + str(stock['lbc']) + "," + \
                            str(datetime.strptime(str(stock['fbt']), "%H%M%S"))[10:] + "," + \
                            str(datetime.strptime(str(stock['lbt']), "%H%M%S"))[10:] + "," + \
                            str(round(stock['fund'] / 100000000, 2)) + "," + str(str(stock['zbc'])) + "," + \
                            str(stock['hybk']) + "," + str(fenmu + str('天') + fenzi + str('板')) + "," + \
                            str(round(stock['fund'] / stock['amount'], 2))

                stocks.append(stock_all.split(","))

            df_uplim = pd.DataFrame(stocks, dtype=object)

            columns = {0: "股票代码", 1: "股票名称", 2: "最新价格", 3: "涨跌幅", 4: "成交额（亿）", 5: "流通市值（亿）", 6: "换手率（%）", 7: "连板天数",
                       8: "首次封板时间", 9: "最终封板时间", 10: "封板资金（亿）", 11: "炸板次数", 12: "所属行业", 13: "涨停统计", 14: '封成比'}
            df_uplim.rename(columns=columns, inplace=True)
            df_uplim = df_uplim.astype({"最新价格": 'float64', "涨跌幅": 'float64', "成交额（亿）": 'float64',
                                               "流通市值（亿）": 'float64',  "换手率（%）": 'float64',  "连板天数": 'int64',
                                               "封板资金（亿）": 'float64',  "炸板次数": 'int64', "封成比": 'float64'})

            df_uplim["股票代码"] = df_uplim["股票代码"].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
            df_uplim["股票名称"] = df_uplim["股票名称"].apply(lambda x: x.replace(" ", ""))

            from_wencai_df = self.get_wencai_data(trade_date[0:4]+"年"+trade_date[4:6]+"月"+trade_date[6:8]+"日"+"涨停", 1)
            df_uplim = pd.merge(df_uplim, from_wencai_df, on='股票名称', left_index=False, right_index=False,
                                        how='left')
            df_uplim.sort_values(by=['连板天数'], ascending=False, inplace=True)

            df_uplim['炸板得分'] = df_uplim['炸板次数'].apply(self.cal_zbc)
            df_uplim['连板得分'] = df_uplim['连板天数'].apply(self.cal_lbc)
            df_uplim['封成比得分'] = df_uplim['封成比'].apply(self.cal_fcb)
            df_uplim['封板时间得分'] = df_uplim['最终封板时间'].apply(self.cal_lbt)

            df_uplim['总分'] = df_uplim[['炸板得分', '连板得分', '封成比得分', '封板时间得分']].sum(axis=1)
            df_uplim.insert(0, u"综合打分", df_uplim['总分'])
            df_uplim = df_uplim.drop(['总分', '炸板得分', '连板得分', '封成比得分', '封板时间得分'], axis=1) # 删除列

        except Exception as e:
            print(e)

        return df_uplim

class THSAskFinanceIf(DataBackend):

    def __init__(self, syslog_obj):
        DataBackend.__init__(self)
        self.syslog = syslog_obj


    def get_wencai_data(self, word='人气排行', total_page=100):
        '''
        获取问财数据
        :return:
        '''
        result = pd.DataFrame()
        for i in range(1, total_page + 1):
            try:
                df = wc.search(word, page_size=i)
                # 如果没有数据推出
                self.syslog.re_print(f"正在获取第{i}页问财数据！\n")
                if df.shape[0] > 0:
                    result = pd.concat([result, df], ignore_index=True)
                else:
                    print('数据获取完成')
                    break
            except:
                pass

        result.rename(columns={"股票简称": "股票名称"}, inplace=True)

        if word == "今日涨停":
            result = result.drop(['涨停明细数据', "涨停"], axis=1)
        return result


