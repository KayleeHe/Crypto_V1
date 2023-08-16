#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import baostock as bs
import numpy as np
import pandas as pd
import sqlite3

def bs_k_data_stock(code_val='sz.000651', start_val='2009-01-01', end_val='2019-06-01',
                    freq_val='d', adjust_val='3'):

    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg

    # 登陆系统
    bs.login()

    # 获取历史行情数据

    if (code_val.find('sz.399')!= -1) or (code_val.find('sh.000')!=-1):
        # 指数无分钟线

        fields = "date,open,high,low,close,volume,amount,pctChg"
        df_bs = bs.query_history_k_data_plus(code_val, fields, start_date=start_val, end_date=end_val,
                                             frequency=freq_val)

        data_list = []

        while (df_bs.error_code == '0') & df_bs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(df_bs.get_row_data())

        result = pd.DataFrame(data_list, columns=df_bs.fields)
        result.replace("", 0, inplace=True)
        result = result.astype({'close': 'float64', 'open': 'float64', 'low': 'float64', 'high': 'float64'})

        result.volume = result.volume.astype('float64')
        result.volume = result.volume / 100  # 单位转换：股-手
        result.amount = result.amount.astype('float64')

        result.date = pd.DatetimeIndex(result.date)
        result.set_index("date", drop=True, inplace=True)
        result.index = result.index.set_names('Date')

        recon_data = {'High': result.high, 'Low': result.low, 'Open': result.open, 'Close': result.close, \
                      'Volume': result.volume, 'amount': result.amount}

        result.pctChg = result.pctChg.astype('float64')
        recon_data['pctChg'] = result.pctChg

    else:
        # 个股指数
        fields = "date,open,high,low,close,volume,pctChg,amount,turn"

        if (freq_val != 'd') and (freq_val != 'w') and (freq_val != 'm'):
            fields = fields.replace('pctChg', 'time') # 分钟线无pctChg 但有time
            fields = fields.replace(',turn', '')  # 分钟线无turn

        df_bs = bs.query_history_k_data_plus(code_val, fields, start_date=start_val, end_date=end_val,
                                             frequency=freq_val,
                                             adjustflag=adjust_val)  # <class 'baostock.data.resultset.ResultData'>

        # frequency="d"取日k线，adjustflag="3"默认不复权，1：后复权；2：前复权

        data_list = []

        while (df_bs.error_code == '0') & df_bs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(df_bs.get_row_data())

        result = pd.DataFrame(data_list, columns=df_bs.fields)
        result.replace("", 0, inplace=True)
        result = result.astype({'close': 'float64', 'open': 'float64', 'low': 'float64', 'high': 'float64'})

        result.volume = result.volume.astype('float64')
        result.volume = result.volume/100 # 单位转换：股-手
        result.amount = result.amount.astype('float64')

        if (freq_val == 'd') or (freq_val == 'w') or (freq_val == 'm'):
            result.date = pd.DatetimeIndex(result.date)
            result.set_index("date", drop=True, inplace=True)
        else:
            result.time = result.time.apply(lambda x: x[:-4])
            result.time = pd.to_datetime(result.time, yearfirst=True, format='%Y%m%d%H%M%S')
            result.set_index("time", drop=True, inplace=True)

        result.index = result.index.set_names('Date')

        recon_data = {'High': result.high, 'Low': result.low, 'Open': result.open, 'Close': result.close, \
                      'Volume': result.volume, 'amount': result.amount}

        if fields.find('pctChg') != -1:
            result.pctChg = result.pctChg.astype('float64')
            recon_data['pctChg'] = result.pctChg

        if fields.find('turn') != -1:
            result.turn = result.turn.astype('float64')
            recon_data['turn'] = result.turn

    df_recon = pd.DataFrame(recon_data)
    # 登出系统
    bs.logout()
    return df_recon

def bs_profit_data_stock(code_val='sh.600000', year_val='2017', quarter_val=2):

    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 查询季频估值指标盈利能力
    profit_list = []
    rs_profit = bs.query_profit_data(code=code_val, year=year_val, quarter=quarter_val)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)

    # 登出系统
    bs.logout()
    return result_profit


def bs_cash_flow_stock(code_val='sh.600000', year_val=2020, quarter_val=2):

    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 季频现金流量
    cash_flow_list = []
    rs_cash_flow = bs.query_cash_flow_data(code=code_val, year=year_val, quarter=quarter_val)
    while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
        cash_flow_list.append(rs_cash_flow.get_row_data())
    df_cash_flow = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)

    df_cash_flow.rename(columns = {"code": "股票代码",  "pubDate":"发布日期", "statDate":"统计截止日",
                                    # 季频现金流量
                                    "CAToAsset": "流动资产除以总资产", "NCAToAsset": "非流动资产除以总资产", "tangibleAssetToAsset": "有形资产除以总资产",
                                    "ebitToInterest": "已获利息倍数", "CFOToOR": "经营活动产生的现金流量净额除以营业收入",
                                    "CFOToNP": "经营性现金净流量除以净利润", "CFOToGr": "经营性现金净流量除以营业总收入",
                                    },  inplace=True)

    # 登出系统
    bs.logout()
    return df_cash_flow

def get_trading_dates(start, end):
    """
    获取所有的交易日
    :param start: 2020-01-01
    :param end: 2020-02-01
    """
    # 登陆系统
    lg = bs.login()

    rs = bs.query_history_k_data_plus("sh.000001",
                                      "date,code,open,high,low,close,preclose,volume,amount,pctChg",
                                      start_date=start, end_date=end, frequency="d")
    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    trading_dates = [date for date in result.date.tolist()]
    # 登出系统
    bs.logout()

    return trading_dates

if __name__ == '__main__':

    # 测试接口
    print(get_trading_dates("2019-01-01", "2020-01-01"))
    """
    ['2019-01-02', '2019-01-03', '2019-01-04',                             元旦 周末2天
    '2019-01-07', '2019-01-08', '2019-01-09', '2019-01-10', '2019-01-11',  周末2天
    '2019-01-14', '2019-01-15', '2019-01-16', '2019-01-17', '2019-01-18',  周末2天
    '2019-01-21', '2019-01-22', '2019-01-23', '2019-01-24', '2019-01-25',  周末2天
    '2019-01-28', '2019-01-29', '2019-01-30', '2019-01-31', '2019-02-01',  周末2天
    '2019-02-11', '2019-02-12', '2019-02-13', '2019-02-14', '2019-02-15',  周末2天
    '2019-02-18', '2019-02-19', '2019-02-20', '2019-02-21', '2019-02-22',  周末2天
    '2019-02-25', '2019-02-26', '2019-02-27', '2019-02-28', '2019-03-01',  2月只有28天 周末2天 
    '2019-03-04', '2019-03-05', '2019-03-06', '2019-03-07', '2019-03-08',  周末2天
    '2019-03-11', '2019-03-12', '2019-03-13', '2019-03-14', '2019-03-15',  周末2天
    '2019-03-18', '2019-03-19', '2019-03-20', '2019-03-21', '2019-03-22',  周末2天
    '2019-03-25', '2019-03-26', '2019-03-27', '2019-03-28', '2019-03-29',  周末2天
    '2019-04-01', '2019-04-02', '2019-04-03', '2019-04-04',                清明节 周末2天
    '2019-04-08', '2019-04-09', '2019-04-10', '2019-04-11', '2019-04-12',  周末2天
    '2019-04-15', '2019-04-16', '2019-04-17', '2019-04-18', '2019-04-19',  周末2天
    '2019-04-22', '2019-04-23', '2019-04-24', '2019-04-25', '2019-04-26',  周末2天
    ......
    """
