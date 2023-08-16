#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import pandas as pd
import tushare as ts

from CommIf.SysFile import Base_File_Oper


def basic_code_list(fields_cont = ['ts_code', 'symbol', 'name']):
    # 查询当前所有正常上市交易的股票列表
    try:
        pro = ts.pro_api(Base_File_Oper.read_tushare_token())  # 初始化pro接口
        data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        data = data[data['ts_code'].apply(lambda x: x.find('BJ') < 0)]
        Base_File_Oper.save_tushare_basic(data)
    except Exception as e:
        print(e)
        print("已经加载本地备份股票代码列表代替tushare basic接口数据！")
        data = Base_File_Oper.load_tushare_basic()

    return data.loc[:, fields_cont]

class Tspro_Backend():

    def __init__(self):

        self.tran_col = {"ts_code": u"股票代码", "close": u"当日收盘价",
                    # "turnover_rate": u"换手率%",
                    "turnover_rate_f": u"换手率%",  # 自由流通股
                    "volume_ratio": u"量比", "pe": u"市盈率(总市值/净利润)",
                    "pe_ttm": u"市盈率TTM",
                    "pb": u"市净率(总市值/净资产)",
                    "ps": u"市销率", "ps_ttm": u"市销率TTM",
                    "dv_ratio": u"股息率%",
                    "dv_ttm": u"股息率TTM%",
                    "total_share": u"总股本(万股)",
                    "float_share": u"流通股本(万股)",
                    "free_share": u"自由流通股本(万股)",
                    "total_mv": u"总市值(万元)",
                    "circ_mv": u"流通市值(万元)",
                    "name": u"股票名称",
                    "area": u"所在地域",
                    "list_date": u"上市日期",
                    "industry": u"所属行业"}

        self.filter = [u"换手率%", u"量比", u"市盈率(总市值/净利润)", u"市盈率TTM",
                  u"市净率(总市值/净资产)", u"市销率", u"市销率TTM", u"股息率%",
                  u"股息率TTM%", u"总股本(万股)", u"流通股本(万股)", u"自由流通股本(万股)",
                  u"总市值(万元)", u"流通市值(万元)", u"所在地域", u"上市日期", u"所属行业"]


    def datafame_join(self, date_val):

        # 使用tushare pro的stock_basic和daily_basic
        try:
            df_stbasic = basic_code_list(['ts_code','name','area','industry','list_date'])
        except:
            print("请检查tushare接口-[stock_basic]是否正常！")
            df_stbasic = pd.DataFrame()

        try:
            pro = ts.pro_api(Base_File_Oper.read_tushare_token())  # 初始化pro接口
            df_dybasic = pro.daily_basic(trade_date=date_val)  # "20200614"
            # cols_to_use = df_dybasic.columns.difference(df_stbasic.columns) # pandas版本0.15及之上 找出两个表不同列，然后merge
        except:
            print("请检查tushare接口-[daily_basic]是否正常！")
            df_dybasic = pd.DataFrame()

        if (df_stbasic.empty != True) and (df_dybasic.empty != True): # 两个接口都正常是合并

            df_join = pd.merge(df_stbasic, df_dybasic, on='ts_code', left_index=False, right_index=False,
                         how='outer')
            df_join.drop(['trade_date', 'turnover_rate'], axis=1, inplace=True)

        elif df_stbasic.empty != True: # 仅返回正常的接口

            df_join = df_stbasic

        elif df_dybasic.empty != True: # 仅返回正常的接口

            df_join = df_dybasic

        else:
            df_join = pd.DataFrame()

        df_join.rename(columns=dict(zip(df_join.columns.tolist(), map(self.tran_col.get, df_join.columns.tolist()))),
                  inplace=True)

        return df_join


