#! /usr/bin/env python 
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import pandas as pd

from CommIf.DatHandle import day_down_resample, \
                             day_to_qfq, \
                             day_to_hfq

class Csv_Backend():

    def __init__(self, src):

        if src == "离线自定义数据(导入即用)":

            self.tran_col = {}
            self.filter = []

        else:
            self.tran_col = {}
            self.filter = []

    def load_pick_data(self, path):

        csv_df = pd.read_csv(path, parse_dates=True, index_col=0, encoding='gbk', engine='c',
                             float_precision='round_trip')

        """
        my_df = pd.read_csv(path)

        # 打印得到columns 经筛选后可作为 usecols 参数的内容
        print(list(my_df.columns))
        # 打印得到columns 经筛选后可作为 tran_col 字典的内容
        print(dict(zip(my_df.columns,my_df.columns)))
        """
        """
        csv_df = pd.read_csv(path,
                   usecols=['代码', '名称', '现价', '涨跌', '买价', '卖价', '现量', '均价', '买量', '卖量', '总量',
                            '5分钟___涨幅%', '最高', '最低', '换手%', '量比', '振幅%', '总金额', '开盘金额', '今开',
                            '昨收', '市盈(动)', '细分行业', '地区', '内盘', '外盘', '内外比', '攻击波%', '回头波%',
                            '实体涨幅%', '强弱度%', '活跃度', '笔换手', '笔均量', '开盘换手Z', '流通股(亿)', '流通市值',
                            '总市值', '连涨天', '昨涨幅%', '3日涨幅%', '20日涨幅%', '60日涨幅%', '年初至今%', '年涨停天',
                            '换手Z', '流通市值Z', '流通比例Z', '市盈(TTM)', '市盈(静)', '贝塔系数', '近日指标提示', '开盘%',
                            '最高%', '最低%', '均涨幅%', '财务更新', '上市日期', '总股本(亿)', 'B/A股(亿)', 'H股(亿)',
                            '总资产(亿)', '净资产(亿)','少数股权(亿)', '资产负债率%', '流动资产(亿)', '固定资产(亿)',
                            '无形资产(亿)', '流动负债(亿)', '货币资金(亿)', '存货(亿)', '应收帐款(亿)','预收账款(亿)',
                            '资本公积金(亿)', '营业收入(亿)', '营业成本(亿)', '营业利润(亿)', '投资收益(亿)', '利润总额(亿)',
                            '税后利润(亿)', '净利润(亿)','扣非净利润(亿)', '未分利润(亿)', '经营现金流(亿)', '总现金流(亿)',
                            '股东人数', '人均持股', '人均市值', '利润同比%', '收入同比%', '市净率', '市现率','市销率',
                            '股息率%', '每股收益', '每股净资', '调整后净资', '每股公积', '每股未分配', '每股现金流',
                            '权益比%', '净益率%', '毛利率%', '营业利润率%', '净利润率%', '研发费用(亿)', '员工人数',
                            '当日___净流入', '净买率%', '当日___相对流量%', '当日___超大单', '当日___大单', '当日___中单',
                            '当日___小单', '交易代码'],
                    nrows=4155)

        csv_df.replace({'--  ': 0}, inplace=True)
        csv_df['量比'] = csv_df['量比'].astype('float') # 遇到str类型的数据格式 要转成数值类型才能条件过滤
        """
        return csv_df

    @staticmethod
    def load_stock_data(path, sdate, edate, adjust_val='不复权', period_val='周线'):
        # sdate:datetime格式,获取数据的开始时间
        # edate:datetime格式,获取数据的结束时间

        # sdate.strftime('%Y-%m-%d %H:%M')
        # edate.strftime('%Y-%m-%d %H:%M')

        MAX_DISP_DATA = 1440 # 最大支持1分钟数据-1天

        # read_csv中有个参数chunksize
        # 通过指定一个chunksize分块大小来读取文件
        # 返回的是一个可迭代的对象TextFileReader
        csv_df = pd.read_csv(path, parse_dates=True, index_col=1, encoding='gbk', engine='python', iterator=True, chunksize=5000)

        store_df = []

        for chunk in csv_df:
            store_df.append(chunk)

        temp_df = pd.concat(store_df, axis=0)

        del store_df

        # 对排序相反的csv文件进行处理
        if temp_df.index[0] > temp_df.index[-1]:
            temp_df.sort_index(inplace=True)  # 升序排列

        # 取数据的有效时间范围
        sdate = temp_df.index[0] if sdate < temp_df.index[0] else sdate
        edate = temp_df.index[-1] if edate > temp_df.index[-1] else edate

        # 保证计算复权时数据包含涨跌幅
        if (adjust_val == '前复权' or
            adjust_val == '后复权') and (
                ('Pctchg' in temp_df.columns.tolist()) or
                ('涨跌幅' in temp_df.columns.tolist())):

            if 'Close' not in temp_df.columns.tolist():
                # 为保持于书中的DataFrame格式一致 重命名列名
                recon_data = {'High': temp_df[u"最高价"],
                              'Low': temp_df[u"最低价"],
                              'Open': temp_df[u"开盘价"],
                              'Close': temp_df[u"收盘价"],
                              'Volume': temp_df[u"成交量"],
                              'Pctchg': temp_df[u"涨跌幅"]}
                temp_df = pd.DataFrame(recon_data)

        else:
            adjust_val = '不复权'

            if 'Close' not in temp_df.columns.tolist():
                # 为保持于书中的DataFrame格式一致 重命名列名
                recon_data = {'High': temp_df[u"最高价"],
                              'Low': temp_df[u"最低价"],
                              'Open': temp_df[u"开盘价"],
                              'Close': temp_df[u"收盘价"],
                              'Volume': temp_df[u"成交量"]}

                temp_df = pd.DataFrame(recon_data)

        temp_df.drop(temp_df[(temp_df['Close'] == 0) & (temp_df['Open'] == 0)].index, axis=0, inplace=True)

        if adjust_val == '前复权':
            temp_df = day_to_qfq(temp_df)

        elif adjust_val == '后复权':
            temp_df = day_to_hfq(temp_df)

        else:
            # 无需复权
            pass

        if period_val == '周线':
            temp_df = day_down_resample(temp_df, 'W-FRI')

        if len(temp_df[sdate:edate]) >= MAX_DISP_DATA:
            return temp_df[-MAX_DISP_DATA:]  # 返回指定范围内的数据
        else:
            return temp_df.loc[sdate:edate, ['High', 'Low', 'Open', 'Close', 'Volume']] # 返回指定范围内的数据

        """
        # 为保持于书中的DataFrame格式一致 重命名列名
        recon_data = {'High': csv_df[u"最高价"],
                      'Low': csv_df[u"最低价"],
                      'Open': csv_df[u"开盘价"],
                      'Close': csv_df[u"收盘价"],
                      'Volume': csv_df[u"成交量"]}

        df_stockload = pd.DataFrame(recon_data)
        df_stockload.sort_index(inplace=True)  # 升序排列2002-01-04排第一个

        #          High     Low    Open   Close   Volume
        # count  4585.0  4585.0  4585.0  4585.0  4.6e+03
        # mean   2744.8  2694.6  2719.7  2722.3  7.8e+09
        # std    1166.4  1136.7  1152.6  1153.2  8.2e+09
        # min     823.9   807.8   816.5   818.0  0.0e+00
        # 25%    1436.1  1421.8  1425.8  1427.4  2.7e+09
        # 50%    2832.9  2768.4  2795.8  2803.9  6.3e+09
        # 75%    3594.5  3514.4  3558.7  3558.5  1.0e+10
        # max    5891.7  5815.6  5862.4  5877.2  6.9e+10

        return df_stockload.loc["2019-01-04":"2019-12-31"]
        """

    @staticmethod
    def load_history_st_data(path='', sdate='', edate='', adjust_val='不复权', period_val='日线'):
        # sdate:datetime格式,获取数据的开始时间
        # edate:datetime格式,获取数据的结束时间

        # stock_dat 数据包含涨跌幅,用于复权计算
        stock_dat = pd.read_csv(path, index_col=0, parse_dates=[u"日期"],
                                encoding='GBK',
                                engine='python')  # 文件名中含有中文时使用engine为python

        stock_dat.set_index("日期", drop=True, inplace=True)
        stock_dat.index = stock_dat.index.set_names('Date')
        #stock_dat.index = stock_dat.index.strftime('%Y-%m-%d') # 使用datetime格式,不用转换为字符串

        if len(stock_dat.index) == 0:
            return pd.DataFrame()

        # 取数据的有效时间范围
        sdate = stock_dat.index[0] if sdate < stock_dat.index[0] else sdate
        edate = stock_dat.index[-1] if edate == "" else edate # 如果为空则默认最新数据
        edate = stock_dat.index[-1] if edate > stock_dat.index[-1] else edate

        if stock_dat[(stock_dat['收盘价'] == 0) & (stock_dat['开盘价'] == 0)].empty != True:
            stock_dat.drop(stock_dat[(stock_dat['收盘价'] == 0) & (stock_dat['开盘价'] == 0)].index, axis=0, inplace=True)

        if adjust_val == '前复权':
            stock_dat = day_to_qfq(stock_dat)

        elif adjust_val == '后复权':
            # 计算后复权因子
            stock_dat = day_to_hfq(stock_dat)
        else:
            # 无需复权
            pass

        return stock_dat.loc[sdate:edate] # 返回指定范围内的数据


