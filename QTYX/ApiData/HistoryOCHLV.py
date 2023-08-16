#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import requests
import time
import os
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
#from CommIf.SqliteHandle import DataBase_Sqlite

class HistoryOCHLV():

    def __init__(self, store_path):
        self.store_path = store_path

        self.down_stock_list = self.init_down_path()
        #self.operate_sqlite = DataBase_Sqlite(self.store_path+ u'stock_history.db')

    def init_down_path(self):
        # 数据保存路径
        if not os.path.exists(self.store_path):
            os.mkdir(self.store_path)  # 创建目录
        # 已下载历史行情的股票
        down_stock_list = []
        for _root, _dirs, _files in os.walk(self.store_path):
            down_stock_list = [f.rstrip('.csv') for f in _files if f.endswith('.csv')]
        return down_stock_list

    """
    从网页爬取数据
    @param:url
    @param:max_try_num
    @param:sleep_time
    @return:返回爬取的网页内容
    """
    """
    def get_content_from_internet(self, url, max_try_num = 10, sleep_time = 5):

        is_success = False
        for i in range(max_try_num):
            try:
                content = requests.get(url, timeout = 30)
                content.encoding = 'GBK'
                is_success = True
                break
            except Exception as e:
                print('第{}次下载数据报错,请检查'.format(i+1))
                time.sleep(sleep_time)

        if is_success:
            return content.text.strip()
    """
    """
    根据股票代码，从网易财经下载股票历史行情数据
    :param stock: 单支股票的代码 000001SZ
    :param start: 历史行情数据开始时间，默认'19900101'
    :param end: 历史行情数据结束时间，默认当天
    :return df: 历史行情DataFrame
    """
    """
    def download_stock_hist_from_netease(self, stock, start = '19900101', end = datetime.now().strftime('%Y%m%d')):
        # xxxxxxSZ
        stock_type = stock[6:8]
        stock_symbol = stock[0:6]

        code = '0' + stock_symbol if stock_type == 'SH' else '1' + stock_symbol
        url = 'http://quotes.money.163.com/service/chddata.html?code={0}&start={1}&end={2}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'.format(code, start, end)
        content = self.get_content_from_internet(url)
        content = StringIO(content)
        df = pd.read_csv(content, parse_dates = ["日期"], na_values = 'None')
        df['股票代码'] = df['股票代码'].str.lstrip("'")
        df['股票代码'] = df['股票代码'] + stock_type.upper()
        df.sort_values(by = ['日期'], ascending = True, inplace = True)
        df.reset_index(drop = True, inplace = True)
        return df
    """
    def code_id_map_em(slef) -> dict:
        """
        东方财富-股票和市场代码
        http://quote.eastmoney.com/center/gridlist.html#hs_a_board
        :return: 股票和市场代码
        :rtype: dict
        """
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:1 t:2,m:1 t:23",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df["market_id"] = 1
        temp_df.columns = ["sh_code", "sh_id"]
        code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
        temp_df_sz["sz_id"] = 0
        code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0 t:81 s:2048",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
        temp_df_sz["bj_id"] = 0
        code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["bj_id"])))
        return code_id_dict

    def download_stock_hist_from_eastmoney(self,
            stock: str = "000001SZ",
            start_date: str = "19700101",
            end_date: str = datetime.now().strftime('%Y%m%d'),
    ) -> pd.DataFrame:
        """
        东方财富网-行情首页-沪深京 A 股-每日行情
        http://quote.eastmoney.com/concept/sh603777.html?from=classic
        :param symbol: 股票代码
        :type symbol: str
        :param period: choice of {'daily', 'weekly', 'monthly'}
        :type period: str
        :param start_date: 开始日期
        :type start_date: str
        :param end_date: 结束日期
        :type end_date: str
        :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
        :type adjust: str
        :return: 每日行情
        :rtype: pandas.DataFrame
        """
        period = "daily"
        type = stock[6:8]
        symbol = stock[0:6]
        adjust = ""

        code_id_dict = self.code_id_map_em()
        adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
        period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": period_dict[period],
            "fqt": adjust_dict[adjust],
            "secid": f"{code_id_dict[symbol]}.{symbol}",
            "beg": start_date,
            "end": end_date,
            "_": "1623766962675",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not (data_json["data"] and data_json["data"]["klines"]):
            return pd.DataFrame()
        temp_df = pd.DataFrame(
            [item.split(",") for item in data_json["data"]["klines"]]
        )
        temp_df.columns = [
            "日期",
            "开盘价",
            "收盘价",
            "最高价",
            "最低价",
            "成交量",
            "成交金额",
            "振幅",
            "涨跌幅",
            "涨跌额",
            "换手率",
        ]
        temp_df.index = pd.to_datetime(temp_df["日期"], format='%Y-%m-%d')
        temp_df.reset_index(inplace=True, drop=True)

        temp_df["开盘价"] = pd.to_numeric(temp_df["开盘价"])
        temp_df["收盘价"] = pd.to_numeric(temp_df["收盘价"])
        temp_df["最高价"] = pd.to_numeric(temp_df["最高价"])
        temp_df["最低价"] = pd.to_numeric(temp_df["最低价"])
        temp_df["成交量"] = pd.to_numeric(temp_df["成交量"]) # 成交量单位: 手
        temp_df["成交金额"] = pd.to_numeric(temp_df["成交金额"]) # 成交额单位: 元
        temp_df["振幅"] = pd.to_numeric(temp_df["振幅"]) # 振幅单位: %
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"]) # 涨跌幅单位: %
        temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"]) # 涨跌额单位: 元
        temp_df["换手率"] = pd.to_numeric(temp_df["换手率"]) # 换手率单位: %
        temp_df.sort_values(by = ['日期'], ascending = True, inplace = True)
        temp_df.reset_index(drop = True, inplace = True)
        temp_df.insert(loc=1, column='股票代码', value=symbol + type.upper())
        return temp_df
    """
    def save_to_db(self, df, table_name, sleep_time = 5):

        try:
            self.operate_sqlite.save_table(df, table_name)
            is_success = True
        except Exception as e:
            print('保存SQL表报错!')
            time.sleep(sleep_time)
        return is_success
    """
    """
    def read_from_db(self, table_name):

        df = self.operate_sqlite.read_table(table_name)
        return df
    """
    def save_to_csv(self, df, path, sleep_time = 5):
        """
        保存df到csv文件
        :param:df
        :param:path
        :param:max_try_num
        :return:
        """
        is_success = False

        try:
            df.to_csv(path, encoding = 'GBK')
            is_success = True
        except Exception as e:
            print('保存csv文件报错!')
            time.sleep(sleep_time)
        return is_success

    def get_history_days_stock_data(self, stock_code):
        """
        获取历史行情数据
        :param stock: 单支股票的代码 000001.SZ
        :return:
        """
        res_info = {}
        res_info["code"] = stock_code
        # 如果已下载该股票历史行情数据，即csv文件存在，则更新数据

        stock_code = stock_code.replace('.', '') # 000001.SZ -> 000001SZ

        if stock_code in self.down_stock_list:
            try:
                df = pd.read_csv(self.store_path + stock_code + '.csv', index_col=0, parse_dates=[u"日期"], encoding='GBK',
                                 engine='python') # 文件名中含有中文时使用engine为python
                #df = self.read_from_db(stcok_code)
                # 已经有数据，更新到今日
                if len(df):
                    df.sort_values(by=['日期'], ascending=True, inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    recent_date = df.iloc[-1]['日期']
                    start = recent_date.strftime('%Y%m%d')
                    end = datetime.now().strftime('%Y%m%d')
                    # 至少更新最后一根K线，因为程序是在当天收盘前运行，最后一根K线的数据不完整
                    if start < end:
                        #try:
                        df_new = self.download_stock_hist_from_eastmoney(stock_code, start, end)
                        df = df.append(df_new, ignore_index=True)
                        df["日期"] = pd.to_datetime(df["日期"], format='%Y-%m-%d')
                        df.drop_duplicates(subset=['日期'], keep='last', inplace=True)
                        is_saved = self.save_to_csv(df, self.store_path + stock_code + '.csv')
                        #is_saved = self.save_to_db(df, stcok_code)

                        if is_saved:
                            #print('{0}更新了{1}条数据'.format(stcok_code, df_new.shape[0]))
                            res_info["status"] = "Success"
                            res_info["number"] = df_new.shape[0]
                        #except:
                        #    print(u"反扒出现:{}".format(stcok_code))
                        #    res_info["status"] = "Fail"
                        #    res_info["number"] = "None"
                    else:
                        #print('{0}数据已最新，无需更新'.format(stock_code))
                        res_info["status"] = "Success"
                        res_info["number"] = 0

                else: # 有文件没数据，下载全部数据
                    df = self.download_stock_hist_from_eastmoney(stock_code)
                    is_saved = self.save_to_csv(df, self.store_path + stock_code + '.csv')
                    #is_saved = self.save_to_db(df, stcok_code)

                    if is_saved:
                        #print('{0}更新了{1}条数据'.format(stcok_code, df.shape[0]))
                        res_info["status"] = "Success"
                        res_info["number"] = df.shape[0]

            except Exception as e:
                print('读取csv文件报错！跳过股票{0}:{1}'.format(stock_code, e))
                res_info["status"] = "Fail"
                res_info["number"] = "None"
        # 如果未下载该股票历史行情数据，即csv文件不存在，下载截止今日的历史数据
        else:
            try:
                df = self.download_stock_hist_from_eastmoney(stock_code)
                is_saved = self.save_to_csv(df, self.store_path + stock_code + '.csv')
                #is_saved = self.save_to_db(df, stcok_code)

                if is_saved:
                    #print('{0}更新了{1}条数据'.format(stcok_code, df.shape[0]))
                    res_info["status"] = "Success"
                    res_info["number"] = df.shape[0]
            except:
                print(u"反扒出现:{}".format(stock_code))
                res_info["status"] = "Fail"
                res_info["number"] = "None"

        # 下载行情数据的同时返回RPS所需的涨跌幅数据
        if res_info["status"] == "Success":
            df.set_index("日期", drop=True, inplace=True) # 原始的dataframe索引是序号
            res_info["pct"] = df["涨跌幅"][-120:].fillna(0)
        return res_info

    def update_latest_day_stock_data(self, df_stock_dat):

        res_info = {"status":"Fail", "number":"None"}

        try:
            res_info["code"] = df_stock_dat["股票代码"].replace('.', '')  # 000001.SZ -> 000001SZ
            stock_code = df_stock_dat["股票代码"].replace('.', '')
            df_stock_dat["股票代码"] = stock_code

            df = pd.read_csv(self.store_path + stock_code + '.csv', index_col=0, parse_dates=[u"日期"], encoding='GBK',
                                 engine='python') # 文件名中含有中文时使用engine为python

            if len(df):
                df.sort_values(by=['日期'], ascending=True, inplace=True)
                df.reset_index(drop=True, inplace=True)
                recent_date = df.iloc[-1]['日期']
                start = recent_date.strftime('%Y-%m-%d')
                end = df_stock_dat["日期"]
                # 至少更新最后一根K线，因为程序是在当天收盘前运行，最后一根K线的数据不完整
                if start <= end:
                    # try:
                    df = df.append(df_stock_dat, ignore_index=True)

                    df.drop_duplicates(subset=['日期'], keep='last', inplace=True)

                    if self.save_to_csv(df, self.store_path + stock_code + '.csv'):
                        # print('{0}更新了{1}条数据'.format(stcok_code, df_new.shape[0]))
                        res_info["status"] = "Success"
                        res_info["number"] = df.shape[0]
                    # except:
                    #    print(u"反扒出现:{}".format(stcok_code))
                    #    res_info["status"] = "Fail"
                    #    res_info["number"] = "None"
                else:
                    print('{0}数据已最新，无需更新'.format(stock_code))
                    res_info["status"] = "Success"
                    res_info["number"] = 0

        except Exception as e:
            print(e)
            res_info["status"] = "Fail"
            res_info["number"] = "None"

        # 下载行情数据的同时返回RPS所需的涨跌幅数据
        if res_info["status"] == "Success":
            df.set_index("日期", drop=True, inplace=True) # 原始的dataframe索引是序号
            res_info["pct"] = df["涨跌幅"][-120:].fillna(0)

        return res_info


if __name__ == '__main__':

    test_ochlv = HistoryOCHLV(u"/Users/SHQ/Downloads/Python量化交易课程/专栏课程制作/Python股票量化交易从入门到实践/扩展视频/例程代码/QuantTradeYx_System-Update-A/QTYX/DataFiles/stock_history/")
    stock_zh_a_hist_df = test_ochlv.download_stock_hist_from_eastmoney(stock="000001SZ", start_date="20170301", end_date='20210907')
    print(stock_zh_a_hist_df)

