#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import time
import numpy as np
import pandas as pd
from datetime import datetime,timedelta

from CommIf.SysFile import Base_File_Oper

from MainlyGui.ElementGui.DefDialogs.CommDialog import MessageDialog, ChoiceDialog, CheckBoxesDialog
from MainlyGui.ElementGui.DefDialogs.SpecDialog import TradeConfDialog, HoldConfDialog
from MainlyGui.ElementGui.DefGrid import GridTable

from CommIf.PrintLog import SysLogIf, InfoLogIf
from CommIf.CodePool import ManageTradePool, ManageSelfPool
from CommIf.CodeTable import ManageCodeTable
from CommIf.TimeMgr import TimeTrigger

from urllib import request, parse
import requests
import random
import json
import re
import os
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
import functools

# 邮件发送相关
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib

####################### 参数配置 ########################

CONF_JSON_PATH = os.path.dirname(__file__) + '/ConfigFiles/' # 存放交易条件单的路径
STORE_CSV_PATH = os.path.dirname(__file__) + '/RealData/'  # 实盘数据存储路径 根据自己的存放位置进行配置

CONF_SCAN_TIME = 1 # 扫描时间3s减去2s执行时间
CONF_STORE_CSV = False # True 表示存储实盘数据; False 表示仅做盯盘
CONF_DEBUG_TIME = True # True 表示盘后调试(手动条件当前时间模拟实盘调试); False 表示实盘运行

def auto_send_email(to_address, subject, content, password, server_address, from_address='your_email_address@foxmail.com'):
    """
    :param to_address: 收件箱地址
    :param subject: 邮件主题
    :param content: 邮件内容
    :param from_address: 发件箱地址
    :param password: 授权码,需要在qq邮箱中设置获取 设置教程http://service.mail.qq.com/cgi-bin/help?subtype=1&&no=1001256&&id=28
    :param server_address: 服务器地址
    :return:
    使用qq邮箱发送邮件的程序。一般用于报错提醒，需要去qq邮箱中开通密码
    """
    max_try_num = 5
    try_num = 0

    while True:
        try:
            # 创建一纯文字的实例
            msg = MIMEText(datetime.now().strftime("%m-%d %H:%M:%S") + '\n ' + content)
            msg["Subject"] = subject + ' ' + datetime.now().strftime("%m-%d %H:%M:%S")
            msg["From"] = from_address
            msg["To"] = ';'.join(to_address) # 接收字符串

            username = from_address
            server = smtplib.SMTP(server_address) # SMTP协议默认端口是25
            server.starttls()
            server.login(username, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            print('邮件发送成功')
            break

        except :
            print('邮件发送失败')
            try_num += 1
            if try_num > max_try_num:
                break

# 定义测试代码执行时间的装饰器-三阶
def timeit_test(number=3, repeat=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(repeat):
                start = time.perf_counter()
                for _ in range(number):
                    return func(*args, **kwargs) # 返回被装饰函数值
                elapsed = (time.perf_counter() - start)
                print('Time of {} used: {} '.format(i, elapsed))
        return wrapper
    return decorator

# 爬虫取东方财富网沪深A股股票每日实时行情数据
class RealTimeData():

    pages = 12  # 目前A股的股票数量需要12页

    def __init__(self):
        self.run_func = {"名称": None, "函数": None, "参数": None}

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

    def crawer_daily(self, page):

        # 沪深A股
        #url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb=jQuery112404462275420342996_1542343049719&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty=FCOIATC&js=({data%3A[(x)]%2CrecordsFiltered%3A(tot)})&cmd=C._A&st=(ChangePercent)&sr=-1&p="+str(page)+"&ps=20&_=1542343050897"

        url = "http://75.push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124006808348016960819_1607923077127" \
              "&pn=" + str(page) + "&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23" \
                      "&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f23&_=1607923077268"

        cur_time = datetime.now() # 记录爬虫最近时刻的时间

        req_obj = request.Request(url, headers=self.get_header())
        resp = request.urlopen(req_obj).read().decode(encoding='utf-8')

        #pattern = re.compile(r'data:\[(.*?)\]', re.S).findall(resp)
        pattern = re.compile(r'"diff":\[(.*?)\]', re.S).findall(resp)

        #st_data = pattern[0].split('","')
        st_data = pattern[0].replace("},{", "}walt{").split('walt')
        stocks = []

        for i in range(len(st_data)):

            #stock = st_data[i].replace('"',"").split(",")
            stock = json.loads(st_data[i])

            stock_all = str(stock['f12']) + "," + str(stock['f14']) + "," + str(stock['f2']) + "," + str(stock['f4']) + "," + \
                        str(stock['f3']) + "," + str(stock['f5']) + "," + str(stock['f6']) + "," + str(stock['f7']) + "," + \
                        str(stock['f15']) + "," + str(stock['f16']) + "," + str(stock['f17']) + "," +str(stock['f18']) + "," +\
                        str(stock['f10']) + "," + str(stock['f8']) + "," + str(stock['f9']) + "," + str(stock['f23']) + "," + \
                        str(stock['f20']) + "," + str(stock['f21'])

            stocks.append(stock_all.split(","))

        df = pd.DataFrame(stocks, dtype=object)

        columns = {0: "股票代码", 1: "股票名称", 2: "最新价格", 3: "涨跌额", 4: "涨跌幅", 5: "成交量", 6: "成交额", 7: "振幅", 8: "最高", 9: "最低",
                   10: "今开", 11: "昨收", 12: "量比", 13: "换手率", 14: "市盈率(动态)", 15:"市净率", 16:"总市值", 17:"流通市值"}

        df.rename(columns=columns, inplace=True)

        if cur_time.second%3 == 1:
            df = df.assign(当前时间=(cur_time+timedelta(seconds=-1)).strftime("%Y-%m-%d %H-%M-%S"))
        elif cur_time.second%3 == 2:
            df = df.assign(当前时间=(cur_time+timedelta(seconds=1)).strftime("%Y-%m-%d %H-%M-%S"))
        else:
            df = df.assign(当前时间=(cur_time.strftime("%Y-%m-%d %H-%M-%S")))

        #df.drop([0, 13, 18, 19, 20, 21, 22, 23, 25], axis=1, inplace=True)
        return df

    #《小散量化炒股记｜只花几秒钟！多任务爬虫获取A股每日实时行情数据》
    @timeit_test(number=1, repeat=1)
    def get_daily_thread(self, para=None):

        itr_arg = np.arange(1, self.pages, 1)
        df_daily_stock = pd.DataFrame(dtype=object)

        with ThreadPoolExecutor(max_workers=8) as executor:
            # map_fun 传入的要执行的map函数
            # itr_argn 可迭代的参数
            # result  返回的结果是一个生成器
            results = executor.map(self.crawer_daily, itr_arg)

        for ret in results:
            df_daily_stock = df_daily_stock.append(ret, ignore_index=True)

        df_daily_stock.replace("-", np.nan, inplace=True)
        df_daily_stock = df_daily_stock.astype({'最新价格': 'float64', '涨跌额': 'float64', '涨跌幅': 'float64',
                                              '成交量': 'float64', '成交额': 'float64', '振幅': 'float64',
                                              '最高': 'float64', '最低': 'float64', '今开': 'float64', '昨收': 'float64',
                                              '量比': 'float64', '换手率': 'float64', '市盈率(动态)': 'float64', '市净率': 'float64',
                                              '总市值': 'float64', '流通市值': 'float64'})

        df_daily_stock["股票代码"] = df_daily_stock["股票代码"].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
        df_daily_stock["成交额(万)"] = np.round(df_daily_stock["成交额"]/10000, 2)
        df_daily_stock["总市值(万)"] = np.round(df_daily_stock["总市值"]/10000, 2)
        df_daily_stock["流通市值(万)"] = np.round(df_daily_stock["流通市值"]/10000, 2)
        df_daily_stock = df_daily_stock.drop(['成交额', '总市值', '流通市值'], axis=1)

        return df_daily_stock

    def stock_changes_em(self, symbols: list = ["大笔买入"]) -> pd.DataFrame:
        """
        东方财富-行情中心-盘口异动
        https://quote.eastmoney.com/changes/
        :param symbol: choice of {'火箭发射', '快速反弹', '大笔买入', '封涨停板', '打开跌停板', '有大买盘', '竞价上涨', '高开5日线', '向上缺口', '60日新高', '60日大幅上涨', '加速下跌', '高台跳水', '大笔卖出', '封跌停板', '打开涨停板', '有大卖盘', '竞价下跌', '低开5日线', '向下缺口', '60日新低', '60日大幅下跌'}
        :type symbol: str
        :return: 盘口异动
        :rtype: pandas.DataFrame
        """
        url = "http://push2ex.eastmoney.com/getAllStockChanges"
        symbol_map = {
            "火箭发射": "8201",
            "快速反弹": "8202",
            "大笔买入": "8193",
            "封涨停板": "4",
            "打开跌停板": "32",
            "有大买盘": "64",
            "竞价上涨": "8207",
            "高开5日线": "8209",
            "向上缺口": "8211",
            "60日新高": "8213",
            "60日大幅上涨": "8215",
            "加速下跌": "8204",
            "高台跳水": "8203",
            "大笔卖出": "8194",
            "封跌停板": "8",
            "打开涨停板": "16",
            "有大卖盘": "128",
            "竞价下跌": "8208",
            "低开5日线": "8210",
            "向下缺口": "8212",
            "60日新低": "8214",
            "60日大幅下跌": "8216",
        }
        reversed_symbol_map = {v: k for k, v in symbol_map.items()}

        df_all = pd.DataFrame()

        for sym in symbols:
            params = {
                "type": symbol_map[sym],
                "pageindex": "0",
                "pagesize": "5000",
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "dpt": "wzchanges",
                "_": "1624005264245",
            }
            r = requests.get(url, params=params)
            data_json = r.json()
            temp_df = pd.DataFrame(data_json["data"]["allstock"])
            temp_df["tm"] = pd.to_datetime(temp_df["tm"], format="%H%M%S").dt.time
            temp_df.columns = [
                "时间",
                "股票代码",
                "_",
                "股票名称",
                "板块",
                "相关信息",
            ]
            temp_df = temp_df[
                [
                    "时间",
                    "股票代码",
                    "股票名称",
                    "板块",
                    "相关信息",
                ]
            ]
            temp_df["板块"] = temp_df["板块"].astype(str)
            temp_df["板块"] = temp_df["板块"].map(reversed_symbol_map)

            temp_df["股票代码"] = temp_df["股票代码"].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')

            df_all = df_all.append(temp_df)

        return df_all


class TradeFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        displaySize_shrink = 0.6*displaySize[0], 0.65*displaySize[1]

        # M1 与 M2 横向布局时宽度分割
        self.M1_width = int(displaySize_shrink[0] * 0.1)
        self.M2_width = int(displaySize_shrink[0] * 0.9)
        # M1 纵向100%
        self.M1_length = int(displaySize_shrink[1])

        # M1中S1 S2 S3 纵向布局高度分割
        self.M1S1_length = int(self.M1_length * 0.2)
        self.M1S2_length = int(self.M1_length * 0.2)
        self.M1S3_length = int(self.M1_length * 0.6)

        # 默认样式wx.DEFAULT_FRAME_STYLE含
        # wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, parent=None, title=u'量化软件', size=displaySize_shrink, style=wx.DEFAULT_FRAME_STYLE)

        ################################### 变量初始化 ###################################
        """
        self.treelist_trade, self.treelist_hold = None, None
        self.treelist_pick = {u'交易股票池': self.treelist_trade,
                              u'持有股票池': self.treelist_hold}

        self.treelist_event = {u'交易股票池': self._ev_click_treelist_trade,
                              u'持有股票池': self._ev_click_treelist_hold,}
        """
        # 用于量化工具集成到整体系统中
        self.fun_swframe = Fun_SwFrame

        # 第二层布局
        self.vbox_sizer_a = wx.BoxSizer(wx.VERTICAL)

        # 创建显示参数配置面板
        self.vbox_sizer_a.Add(self._init_text_log(), proportion=1, flag=wx.EXPAND | wx.ALL |wx.CENTER, border=3)
        self.vbox_sizer_a.Add(self._init_nav_notebook(), proportion=2, flag=wx.EXPAND | wx.ALL |wx.CENTER, border=3)
        # 第二层布局
        self.vbox_sizer_b = wx.BoxSizer(wx.VERTICAL)
        # 创建参数区面板
        self.vbox_sizer_b.Add(self._init_para_panel(), proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        # 创建表格
        self.vbox_sizer_b.Add(self._init_grid_pk(), proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        ################################### 第一层布局 ###################################
        # 第一层布局
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_a, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        #self.HBoxPanelSizer.Add(self._init_tree_notebook(), proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_b, proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效

        self.syslog = SysLogIf(self.sys_log_tx)

        ################################### 加载股票代码表 ###################################
        self.code_table = ManageCodeTable(self.syslog)
        self.code_table.update_stock_code()

        ################################### 加载交易股票池 ###################################
        self.trade_pool = ManageTradePool(self.syslog, "交易股票池", "trade_para.json")
        self.grid_trade.SetTable(self.trade_pool.load_name_code(), ["交易股", "代码"])

        ################################### 加载持有股票池 ###################################
        self.hold_pool = ManageTradePool(self.syslog, "持有股票池", "hold_para.json")
        self.grid_hold.SetTable(self.hold_pool.load_name_code(), ["交易股", "代码"])

        ################################### 加载自选股票池 ###################################
        self.code_pool = ManageSelfPool(self.syslog)

        ################################### 创建实盘定时器 ###################################
        self.real_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._ev_int_timer, self.real_timer) # 绑定一个定时器事件
        self.start_scheduler = TimeTrigger(self.syslog)
        self.rt_data_if = RealTimeData()

        # 创建状态栏
        self._init_status_bar()

    def _init_nav_notebook(self):

        # 创建参数区面板
        self.NavNoteb = wx.Notebook(self)
        self.NavNoteb.AddPage(self._init_grid_trade(self.NavNoteb), "交易池索引")
        self.NavNoteb.AddPage(self._init_grid_hold(self.NavNoteb), "持有池索引")

        return self.NavNoteb

    """
    def _init_tree_notebook(self):
        # 创建列表树面板
        self.TreeNoteb = wx.Notebook(self)

        self.TreeTradePanel = wx.Panel(self.TreeNoteb, -1) # 交易 trade
        self.TreeHoldPanel = wx.Panel(self.TreeNoteb, -1) # 持有 hold

        self.TreeNoteb.AddPage(self._init_treelist_pick(self.TreeTradePanel, "交易股票池"), "交易") # trade
        self.TreeNoteb.AddPage(self._init_treelist_pick(self.TreeHoldPanel, "持有股票池"), "持有") # hold

        return self.TreeNoteb
    """
    """
    def _init_treelist_pick(self, sub_panel, label): # 自选股票池

        # 加载本地股票池 -- 在初始化最后一步刷新时处理
        # 创建一个 treeListCtrl object
        self.treelist_pick[label] = CollegeTreeListCtrl1(parent=sub_panel, size=(400, 450),
                                                 tree_labels=[u'名称', u'代码', u'最新价格', u'每股净资产'],
                                                 tree_widths=[150, 100, 70, 80])

        self.treelist_pick[label].Bind(wx.EVT_TREE_SEL_CHANGED, self.treelist_event[label])

        return sub_panel
    """
    """
    def _refresh_treelist_pick(self, label): # 自选股票池

        # 加载本地股票池
        self._treelist_pick_creat(label, self.datafame_join)

        self.treelist_pick[label].refDataShow(label, self.pick_colleges)  # TreeCtrl显示数据接口
    """

    def _init_text_log(self):

        self.sys_info_box = wx.StaticBox(self, -1, u'系统日志')
        self.sys_info_sizer = wx.StaticBoxSizer(self.sys_info_box, wx.VERTICAL)

        # 创建并初始化系统日志框
        self.sys_log_tx = wx.TextCtrl(self, -1, "更新日志:\n", style=wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY, size=(self.M1_width, self.M1S1_length))
        self.sys_log_tx.SetMaxLength(0)
        #self.sys_log_tx.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.sys_info_sizer.Add(self.sys_log_tx, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        return self.sys_info_sizer

    def _init_para_panel(self):

        self.ParaPanel = wx.Panel(self, -1)

        # 任务参数
        stock_para_box = wx.StaticBox(self.ParaPanel, -1, u'任务参数')
        stock_para_sizer = wx.StaticBoxSizer(stock_para_box, wx.HORIZONTAL)

        # 子参数——配置参数
        self.cfg_pools_box = wx.StaticBox(self.ParaPanel, -1, u'实盘监测范围')
        self.cfg_pools_sizer = wx.StaticBoxSizer(self.cfg_pools_box, wx.HORIZONTAL)
        self.cfg_pools_cmbo = wx.ComboBox(self.ParaPanel, -1, u"全市场股票",
                                          choices=[u"全市场股票", u"交易&持有池"],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)
        self.cfg_pools_sizer.Add(self.cfg_pools_cmbo, proportion=0,
                                 flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 搜索参数——输入查询内容
        self.search_info_box = wx.StaticBox(self.ParaPanel, -1, u'搜索栏')
        self.search_info_sizer = wx.StaticBoxSizer(self.search_info_box, wx.VERTICAL)
        self.search_info_input = wx.TextCtrl(self.ParaPanel, -1, "华友钴业", style=wx.TE_PROCESS_ENTER)
        self.search_info_sizer.Add(self.search_info_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 导入股票池按钮
        self.import_pool_but = wx.Button(self.ParaPanel, -1, "导入股票池")
        self.import_pool_but.Bind(wx.EVT_BUTTON, self._ev_import_pool)  # 绑定按钮事件

        # 子参数——扫描时间
        self.scan_interval_box = wx.StaticBox(self.ParaPanel, -1, u'实盘扫描间隔(秒)')
        self.scan_interval_sizer = wx.StaticBoxSizer(self.scan_interval_box, wx.HORIZONTAL)
        self.scan_interval_cmbo = wx.ComboBox(self.ParaPanel, -1, u"5",
                                          choices=[u"5", u"15", u"30", u"60"],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)
        self.scan_interval_sizer.Add(self.scan_interval_cmbo, proportion=0,
                                 flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 子参数——是否发送邮件
        self.send_email_box = wx.StaticBox(self.ParaPanel, -1, u'发送邮件开关')
        self.send_email_sizer = wx.StaticBoxSizer(self.send_email_box, wx.VERTICAL)
        self.send_email_chk = wx.CheckBox(self.ParaPanel, label='使能')
        self.send_email_sizer.Add(self.send_email_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 开始实盘按钮
        self.real_monitor_but = wx.Button(self.ParaPanel, -1, "开始实盘")
        self.real_monitor_but.Bind(wx.EVT_BUTTON, self._ev_monitor_task)  # 绑定按钮事件

        stock_para_sizer.Add(self.cfg_pools_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.search_info_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.import_pool_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.scan_interval_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.send_email_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.real_monitor_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        self.ParaPanel.SetSizer(stock_para_sizer)

        return self.ParaPanel

    def data_to_grid(self, df):

        self.grid = wx.grid.Grid(self, -1)

        if df.empty != True:
            df.insert(0, u"基金机构", df.index)
            self.list_columns = df.columns.tolist()
            self.grid.CreateGrid(df.shape[0], df.shape[1])

            for col, series in df.iteritems():  # 将DataFrame迭代为(列名, Series)对
                m = self.list_columns.index(col)
                self.grid.SetColLabelValue(m, col)
                for n, val in enumerate(series):
                    self.grid.SetCellValue(n, m, str(val))
                self.grid.AutoSizeColumn(m, True)  # 自动调整列尺寸

    def _init_grid_pk(self):

        # 初始化选股表格
        self.grid_pk = GridTable(parent=self)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_cell_lclick_pkcode, self.grid_pk)

        # 获取自选股票池行情数据
        self.df_use = pd.DataFrame()

        return self.grid_pk

    def _init_grid_trade(self, subpanel):
        # 初始化交易池表格
        self.grid_trade = GridTable(parent=subpanel, nrow=0, ncol=2)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_click_trcode, self.grid_trade)
        return self.grid_trade

    def _init_grid_hold(self, subpanel):
        # 初始化持有池表格
        self.grid_hold = GridTable(parent=subpanel, nrow=0, ncol=2)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_click_hdcode, self.grid_hold)
        return self.grid_hold

    def _ev_click_trcode(self, event): # 点击交易池股票代码

        # 收集股票池中名称和代码
        st_code = self.grid_trade.GetCellValue(event.GetRow(), 1)
        st_name = self.grid_trade.GetCellValue(event.GetRow(), 0)

        select_msg = ChoiceDialog(u"自选股点击处理事件", [u"从交易池中剔除",
                                                 u"查看交易参数"])
        if select_msg == u"查看交易参数":
            st_info = self.trade_pool.load_trade_stock(st_name)

            trade_paras = TradeConfDialog(self, st_code, st_name,
                                          st_info["close"], st_info["price"],
                                          st_info["direct"], st_info["amount"])
            trade_paras.Centre()

            if trade_paras.ShowModal() == wx.ID_OK:
                self.trade_pool.update_increase_st(trade_paras.execute_paras())
                self.grid_trade.SetTable(self.trade_pool.load_name_code(), ["交易池", "代码"])
                MessageDialog("实盘交易中使用远程提醒功能,请确认已经填写邮箱信息")

        elif select_msg == u"从交易池中剔除":
            self.trade_pool.delete_one_st(st_name)
            self.grid_trade.SetTable(self.trade_pool.load_name_code(), ["交易池", "代码"])
        else:
            pass

    def _ev_click_hdcode(self, event): # 点击持有池股票代码

        # 收集股票池中名称和代码
        st_code = self.grid_hold.GetCellValue(event.GetRow(), 1)
        st_name = self.grid_hold.GetCellValue(event.GetRow(), 0)

        select_msg = ChoiceDialog(u"自选股点击处理事件", [u"从持有池中剔除",
                                                 u"查看持有参数"])
        if select_msg == u"查看持有参数":
            st_info = self.hold_pool.load_trade_stock(st_name)

            hold_paras = HoldConfDialog(self, st_code, st_name, st_info["exceed"], st_info["retreat"],
                                              st_info["price"], st_info["highest"])
            hold_paras.Centre()
            if hold_paras.ShowModal() == wx.ID_OK:
                self.hold_pool.update_increase_st(hold_paras.execute_paras())
                self.grid_hold.SetTable(self.hold_pool.load_name_code(), ["交易池", "代码"])
                MessageDialog("实盘交易中使用远程提醒功能,请确认已经填写邮箱信息")

        elif select_msg == u"从持有池中剔除":
            self.hold_pool.delete_one_st(st_name)
            self.grid_hold.SetTable(self.hold_pool.load_name_code(), ["交易池", "代码"])
        else:
            pass

    def _ev_cell_lclick_pkcode(self, event):  # 点击选股表中股票代码

        # 收集表格中的列名
        col_label = self.grid_pk.GetColLabelValue(event.GetCol())

        if col_label == "股票代码" :
            # 收集表格中的单元格
            try:
                st_code = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_name = self.code_table.get_name(st_code)
            except:
                MessageDialog("股票代码不在存储表中！检查是否为新股/退市等情况！")

        elif col_label == "股票名称":
            # 收集表格中的单元格
            try:
                st_name = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_code = self.code_table.get_code(st_name)
            except:
                MessageDialog("股票名称不在存储表中！检查是否为新股/退市等情况！")

        else:
            MessageDialog("请点击股票代码或股票名称！")
            st_name, st_code = '', ''

        select_des = ChoiceDialog(u"选择添加到交易/持有股票池", [u"交易股票池",u"持有股票池"])

        if st_name != "" and st_code != "":

            if select_des == u"交易股票池":
                preclose = self.df_use.loc[self.df_use["股票代码"] == st_code, "最新价格"].values[0]
                trade_paras = TradeConfDialog(self, st_code, st_name, preclose, preclose, "买", "1000", "自动交易参数配置")
                trade_paras.Centre()
                if trade_paras.ShowModal() == wx.ID_OK:
                    self.trade_pool.update_increase_st(trade_paras.execute_paras())
                    MessageDialog("实盘交易中使用远程提醒功能,请确认已经填写邮箱信息")
                    self.grid_trade.SetTable(self.trade_pool.load_name_code(), ["交易池", "代码"])

            elif select_des == u"持有股票池":
                preclose = self.df_use.loc[self.df_use["股票代码"] == st_code, "最新价格"].values[0]
                highest = self.df_use.loc[self.df_use["股票代码"] == st_code, "最高"].values[0]
                hold_paras = HoldConfDialog(self, st_code, st_name, 8, 5, preclose, highest)
                hold_paras.Centre()
                if hold_paras.ShowModal() == wx.ID_OK:
                    self.hold_pool.update_increase_st(hold_paras.execute_paras())
                    MessageDialog("实盘交易中使用远程提醒功能,请确认已经填写邮箱信息")
                    self.grid_hold.SetTable(self.hold_pool.load_name_code(), ["交易池", "代码"])
            else:
                pass

    def refresh_grid(self, df, back_col=""):
        self.grid_pk.SetTable(df, self.tran_col)
        self.grid_pk.SetSelectCol(back_col)

    def _ev_import_pool(self, event):

        self.df_use = self.rt_data_if.get_daily_thread()

        if self.df_use.empty == True:
            MessageDialog("选股数据为空！请检查数据源是否有效！\n")
        else:
            # 数据获取正常后执行

            self.filter = self.df_use.columns.tolist()
            self.tran_col = dict(zip(self.df_use.columns.tolist(), self.filter))

            df_pool = pd.DataFrame()
            for code in self.code_pool.load_pool_stock().values():
                # code 是 tushare xxxxxx.SZ/xxxxxx.SH 格式
                df_pool = df_pool.append(self.df_use[self.df_use["股票代码"] == code],
                                                   ignore_index=True)
            self.df_use = df_pool
            self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

    """
    def _ev_click_treelist_trade(self, event):
        pass
    """
    """
    def _ev_click_treelist_hold(self, event):
        pass
    """

    def _init_status_bar(self):

        self.statusBar = self.CreateStatusBar() # 创建状态条
        # 将状态栏分割为3个区域,比例为2:1
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-2, -1, -1])
        t = time.localtime(time.time())
        self.SetStatusText("公众号：元宵大师带你用Python量化交易", 0)
        self.SetStatusText("当前版本：%s" % Base_File_Oper.load_sys_para("sys_para.json")["__version__"], 1)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 2)

    def _ev_int_timer(self, event):

        self.real_timer.Stop()  # 关闭定时器

        if self.start_scheduler.trigger_once(CONF_DEBUG_TIME) == True:

            self.df_rt = self.rt_data_if.run_func["函数"](self.rt_data_if.run_func["参数"])

            if self.df_rt.empty == True:
                MessageDialog("选股数据为空！请检查数据源是否有效！\n")
            else:
                # 数据获取正常后执行

                if self.rt_data_if.run_func["名称"] == "实盘行情":
                    if CONF_STORE_CSV:
                        self.df_rt.to_csv(Path(STORE_CSV_PATH + u"{}.csv".format(self.df_rt["当前时间"].values[0])),
                                           columns=self.df_use.columns, index=True, encoding='GBK')
                    self.monitor_stock(self.df_rt)

                self.filter = self.df_rt.columns.tolist()
                self.tran_col = dict(zip(self.df_rt.columns.tolist(), self.filter))

                if self.cfg_pools_cmbo.GetStringSelection() == "交易&持有池":

                    df_pool = pd.DataFrame()
                    # 加载配置文件
                    trade_para_dict = Base_File_Oper.load_sys_para("trade_para.json")

                    for name, val in trade_para_dict.items():
                        code = val['code']
                        # code 是 tushare xxxxxx.SZ/xxxxxx.SH 格式
                        df_pool = df_pool.append(self.df_rt[self.df_rt["股票代码"] == code],
                                                 ignore_index=True)

                    # 加载配置文件
                    hold_para_dict = Base_File_Oper.load_sys_para("hold_para.json")

                    for name, val in hold_para_dict.items():
                        code = val['code']
                        # code 是 tushare xxxxxx.SZ/xxxxxx.SH 格式
                        df_pool = df_pool.append(self.df_rt[self.df_rt["股票代码"] == code],
                                                 ignore_index=True)
                    if df_pool.empty != True:
                        self.refresh_grid(df_pool, df_pool.columns.tolist()[0])
                else:
                    self.refresh_grid(self.df_rt, self.df_rt.columns.tolist()[0])

        self.real_timer.Start(int(self.scan_interval_cmbo.GetStringSelection()) * 1000)  # 启动定时器

    def _ev_monitor_task(self, event):

        if self.real_monitor_but.GetLabel() == u"开始实盘":

            if ChoiceDialog("选择实盘监测数据", [u"盘口异动", u"实时行情"]) == u"盘口异动":

                checkboxes_dialog = CheckBoxesDialog(self, title="收集盘口异动数据类型",
                                                      items = [u"火箭发射", u"快速反弹", u"大笔买入", u"封涨停板", u"打开跌停板",
                                                      u"有大买盘", u"竞价上涨", u"高开5日线", u"向上缺口", u"60日新高",
                                                      u"60日大幅上涨", u"加速下跌", u"高台跳水", u"大笔卖出", u"封跌停板",
                                                      u"打开涨停板", u"有大卖盘", u"竞价下跌", u"低开5日线", u"向下缺口",
                                                      u"60日新低", u"60日大幅下跌"])
                checkboxes_dialog.Centre()
                checkboxes_dialog.ShowModal()

                self.rt_data_if.run_func["名称"] = u"盘口异动"
                self.rt_data_if.run_func["函数"] = self.rt_data_if.stock_changes_em
                self.rt_data_if.run_func["参数"] = checkboxes_dialog.feedback_paras()
            else:
                self.rt_data_if.run_func["名称"] = u"实时行情"
                self.rt_data_if.run_func["函数"] = self.rt_data_if.get_daily_thread

            self.real_monitor_but.SetLabel(u"停止实盘")
            self.real_timer.Start(int(self.scan_interval_cmbo.GetStringSelection())*1000) # 启动定时器

        elif self.real_monitor_but.GetLabel() == u"停止实盘":
            self.real_monitor_but.SetLabel(u"开始实盘")
            self.real_timer.Stop() # 关闭定时器

        else:
            pass

    def monitor_stock(self, df_real):

        # 监测买卖列表中的股票
        send_cont = ""
        trigger_name = []

        # 加载配置文件
        trade_para_dict = Base_File_Oper.load_sys_para("trade_para.json")

        for name, val in trade_para_dict.items():
            df_st = df_real[df_real["股票代码"] == val['code']]

            if df_st.empty != True:
                if val['direct'] == "买":
                    if df_st['最新价格'].values[0] <= val['price']:
                        send_cont += f"{name} {val['code']} 价格为{df_st['最新价格'].values[0]},已经低于买入设定值 {val['price']} ;\n"
                        if val['auto_trade'] == True:
                            print("自动交易需调试交易环境，查看公众号《小散量化炒股记｜要克服人性弱点？激活股票全自动化交易！》")
                        trigger_name.append(name)

                elif val['direct'] == "卖":
                    if df_st['最新价格'].values[0] >= val['price']:
                        send_cont += f"{name} {val['code']} 价格为{df_st['最新价格'].values[0]},已经超过卖出设定值 {val['price']};\n"
                        if val['auto_trade'] == True:
                            print("自动交易需调试交易环境，查看公众号《小散量化炒股记｜要克服人性弱点？激活股票全自动化交易！》")
                        trigger_name.append(name)
                else:
                    pass
            else:
                print(f"{val['code']} DataFrame数据不存在!")

        if (send_cont != "") and (self.send_email_chk.GetValue() == True):

            # 加载配置文件
            sys_para_dict = Base_File_Oper.load_sys_para("sys_para.json")

            auto_send_email(sys_para_dict['mailbox']['to_address'],
                            '主人！你实时监测的股票有最新消息！',
                            send_cont,
                            sys_para_dict['mailbox']['password'],  # Password: 此为假密码, 请填写真实的密码 pdtsykxtcazcbajf / achijymjnpkybfjj
                            'smtp.qq.com',  # smtp.163.com
                             from_address=sys_para_dict['mailbox']['from_address']) #
            # 邮箱触发完成后会将交易文件中的命令删除, 避免重复触发
            for name in trigger_name:
                #trade_para_dict.pop(name)
                #Base_File_Oper.save_sys_para("trade_para.json", trade_para_dict)
                self.trade_pool.delete_one_st(name)
                self.grid_trade.SetTable(self.trade_pool.load_name_code(), ["交易池", "代码"])

        # 监测持有止赢止损列表中的股票
        send_cont = ""
        trigger_name = []

        # 加载配置文件
        hold_para_dict = Base_File_Oper.load_sys_para("hold_para.json")

        for name, val in hold_para_dict.items():
            df_st = df_real[df_real["股票代码"] == val['code']]
            if df_st.empty != True:
                if df_st['最新价格'].values[0] > val['highest']:
                    hold_para_dict[name]['highest'] = df_st['最新价格'].values[0]
                    Base_File_Oper.save_sys_para("hold_para.json", hold_para_dict)

                if df_st['最新价格'].values[0] < val['highest'] * (1-val['retreat']/100):
                    # 止损
                    send_cont += f"{name} {val['code']} 价格为{df_st['最新价格'].values},已经低于止损设定值 {val['retreat']} ;\n"
                    if val['auto_trade'] == True:
                        print("自动交易需调试交易环境，查看公众号《小散量化炒股记｜要克服人性弱点？激活股票全自动化交易！》")
                    trigger_name.append(name)

                elif df_st['最新价格'].values[0] > val['price'] * (1+val['exceed']/100):
                    # 止盈
                    send_cont += f"{name} {val['code']} 价格为{df_st['最新价格'].values},已经高于止盈设定值 {val['exceed']}% ;\n"
                    if val['auto_trade'] == True:
                        print("自动交易需调试交易环境，查看公众号《小散量化炒股记｜要克服人性弱点？激活股票全自动化交易！》")
                    trigger_name.append(name)
                else:
                    pass
            else:
                print(f"{val['code']} DataFrame数据不存在!")

        if (send_cont != "") and (self.send_email_chk.GetValue() == True):

            sys_para_dict = Base_File_Oper.load_sys_para("sys_para.json")

            auto_send_email(sys_para_dict['mailbox']['to_address'],
                            '主人！你实时监测的股票有最新消息！',
                            send_cont,
                            sys_para_dict['mailbox']['password'],  # Password: 此为假密码, 请填写真实的密码 pdtsykxtcazcbajf / achijymjnpkybfjj
                            'smtp.qq.com',  # smtp.163.com
                             from_address=sys_para_dict['mailbox']['from_address']) #
            # 邮箱触发完成后会将交易文件中的命令删除, 避免重复触发
            for name in trigger_name:
                #hold_para_dict.pop(name)
                #Base_File_Oper.save_sys_para("hold_para.json", hold_para_dict)
                self.hold_pool.delete_one_st(name)
                self.grid_hold.SetTable(self.hold_pool.load_name_code(), ["交易池", "代码"])
