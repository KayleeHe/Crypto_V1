#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import re
import wx
import wx.adv
import wx.grid
import wx.html2
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import webbrowser
from importlib import reload
from datetime import datetime, timedelta
import queue
import platform

from MainlyGui.ConfFrame import ConfFrame
from MainlyGui.TradeFrame import TradeFrame

from MainlyGui.ElementGui.DefPanel import (
    SubGraphs,
    Sys_Panel
)
from MainlyGui.ElementGui.DefEchart import (
    WebGraphs
)
from MainlyGui.ElementGui.DefTreelist import (
    CollegeTreeListCtrl, CollegeTreeListCtrl2
)
from MainlyGui.ElementGui.DefGrid import (
    GridTable
)
from MainlyGui.ElementGui.DefEchart import (
    Pyechart_Drive
)
from MainlyGui.ElementGui.DefDialogs.CommDialog import MessageDialog, ImportFileDiag, ChoiceDialog

from MainlyGui.ElementGui.DefDialogs.SpecDialog import (
    ScanDialog, UserDialog, GroupPctDiag, GroupTrendDiag, BrowserF10,
    WebDialog, DouBottomDialog, RpsTopNDialog, RpsTrackDialog, BreakBottomDialog, ViewGripDiag,
    CondSelDialog, DateInputDialog, MsgInputDialog, MultMaRiseDialog, NeedleBottomDialog, NewHighBreakDialog, IndustryCountDialog
)
from MainlyGui.ElementGui.DefDialogs.ParaDialog import (MarketGraphDialog, BacktGraphDialog, SelectModeDialog)

from MainlyGui.ElementGui.DefProgress import ProgressBarDialog, DownloadDataThread

from MainlyGui.ElementGui.DefAnimation import KlineRunDialog, RpsCompeteDialog

from MainlyGui.ElementGui.DefListBox import ClassifySelectDiag

from MainlyGui.ElementGui.DefListCtrl import ViewListDiag

from ApiData.FromSql import (
    ReadFundDatFromSql
)
from ApiData.SpecialData import UpLimitImp, DailyIndImp, NorthMoneyImp, THSAskFinanceIf

from ApiData.Csvdata import (
    Csv_Backend
)

# 分离控件事件中调用的子事件
from EventEngine.DefEvent import (
    EventHandle
)
from StrategyGath.IndicateGath import Base_Indicate_Group
from StrategyGath.StrategyGath import Base_Strategy_Group
from StrategyGath.PattenGath import Base_Patten_Group

from CommIf.SysFile import Base_File_Oper
from CommIf.CodeTable import ManageCodeTable
from CommIf.CodePool import ManageSelfPool, ManageTradePool
from CommIf.PrintLog import SysLogIf, InfoLogIf
from CommIf.RemoteInfo import auto_send_email
from CommIf.SqliteHandle import DataBase_Sqlite
from CommIf.MultiThread import CrawlerThread

from ApiData.HistoryOCHLV import HistoryOCHLV

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 创建本地存储路径
data_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/stock_history/'
pickout_path = os.path.dirname(os.path.dirname(__file__)) + '/ConfigFiles/'

q_paras = queue.Queue(5000)
q_results = queue.Queue(5000)

class UserFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        # M1 与 M2 横向布局时宽度分割
        self.M1_width = int(displaySize[0] * 0.1)
        self.M2_width = int(displaySize[0] * 0.9)
        # M1 纵向100%
        self.M1_length = int(displaySize[1])

        # M1中S1 S2 S3 纵向布局高度分割
        self.M1S1_length = int(self.M1_length * 0.2)
        self.M1S2_length = int(self.M1_length * 0.2)
        self.M1S3_length = int(self.M1_length * 0.6)

        # 默认样式wx.DEFAULT_FRAME_STYLE含
        # wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, parent=None, title=u'股票量化分析软件 QTYX-Master',
                          size=displaySize, style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        # 用于量化工具集成到整体系统中
        self.fun_swframe = Fun_SwFrame

        # 多子图布局对象
        self.FlexGridSizer = None

        # 存储单个行情数据
        self.stock_dat = pd.DataFrame()
        # 存储单个回测数据
        self.backt_dat = pd.DataFrame()

        # 获取系统信息 Windows系统下运行返回 'Windows'，Linux返回'Linux' MacOS返回'Darwin'
        #print(platform.system())

        # 存储策略函数
        self.function = ''

        # 初始化事件调用接口
        self.EventHandle = EventHandle()
        self.call_method = self.EventHandle.call_method
        self.event_task = self.EventHandle.event_task

        # 添加参数布局
        self.vbox_sizer_a = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        self.vbox_sizer_a.Add(self._init_log_notebook(), proportion=1, flag=wx.EXPAND | wx.ALL |wx.CENTER, border=1)
        #self.vbox_sizer_a.Add(self._init_gauge_bar(), proportion=1, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)
        self.vbox_sizer_a.Add(self._init_listbox_mult(), proportion=1, flag=wx.EXPAND | wx.ALL |wx.CENTER, border=1)
        self.vbox_sizer_a.Add(self._init_nav_notebook(), proportion=2, flag=wx.EXPAND | wx.ALL |wx.CENTER, border=1)

        #self.vbox_sizer_a.Add(self._init_grid_pl(), proportion=5, flag=wx.EXPAND | wx.BOTTOM, border=5)

        # 加载配置文件
        firm_para = Base_File_Oper.load_sys_para("firm_para.json")
        back_para = Base_File_Oper.load_sys_para("back_para.json")

        # 创建显示区面板
        self.DispPanel = Sys_Panel(self, **firm_para['layout_dict']) # 自定义
        self.BackMplPanel = Sys_Panel(self, **back_para['layout_dict']) # 自定义
        self.DispPanelA = self.DispPanel

        # 此处涉及windows和macos的区别
        sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "windows":
            try:
                # WIN环境下兼容WEB配置
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION",
                                     0, winreg.KEY_ALL_ACCESS)  # 打开所有权限
                # 设置注册表python.exe 值为 11000(IE11)
                winreg.SetValueEx(key, 'python.exe', 0, winreg.REG_DWORD, 0x00002af8)
            except:
                # 设置出现错误
                MessageDialog("WIN环境配置注册表中浏览器兼容显示出错,检查是否安装第三方库【winreg】")

        # 第二层布局
        self.vbox_sizer_b = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        self.vbox_sizer_b.Add(self._init_para_notebook(), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)  # 添加行情参数布局
        self.vbox_sizer_b.Add(self._init_grid_pk(), proportion=10, flag=wx.EXPAND | wx.BOTTOM, border=5)

        # 第一层布局
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self._init_toolbar(), proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_a, proportion=3, border=1, flag=wx.EXPAND | wx.ALL)
        self.HBoxPanelSizer.Add(self.vbox_sizer_b, proportion=20, border=1, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer) # 使布局有效

        # 初始化全部页面
        self.switch_main_panel(self.grid_pk, self.BackMplPanel, False)
        self.switch_main_panel(self.BackMplPanel, self.DispPanel, True)  # 等类型替换

        ################################### 辅助配置 ###################################
        self.syslog = SysLogIf(self.sys_log_tx)
        self.patlog = InfoLogIf(self.patten_log_tx)

        ################################### 变量初始化 ###################################
        self.failed_list = [] # 更新失败列表

        self.start_time = time.perf_counter()
        self.elapsed_time = time.perf_counter()
        self.dialog = None
        self.urgent_stop_flag = False
        ################################### 加载股票代码表 ###################################
        self.code_table = ManageCodeTable(self.syslog)
        self.code_table.update_stock_code()

        ################################### 加载交易股票池 ###################################
        self.trade_pool = ManageTradePool(self.syslog, "交易股票池", "trade_para.json")

        # 获取股票代码
        self.stock_tree_info = dict(zip(self.code_table.stock_codes.values(), self.code_table.stock_codes.keys()))
        self.total_len = len(self.code_table.stock_codes.values()) #df_basic.ts_code.values
        self.treeListStock.refDataShow(self.stock_tree_info) # TreeCtrl显示数据接口

        ################################### 加载自选股票池 ###################################
        self.self_pool = ManageSelfPool(self.syslog)

        group_dict = self.self_pool.load_pool_group()
        self._update_analyse_list(list(map(lambda x: group_dict[x]+"|"+x, group_dict)))
        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        self._init_status_bar()
        self._init_menu_bar()
        self.Bind(wx.EVT_CLOSE, self._ev_switch_menu)
        self.Center()

    def _init_toolbar(self):

        store_path = os.path.dirname(os.path.dirname(__file__))+'/ConfigFiles/'

        toolbar = wx.ToolBar(self, style = wx.TB_VERTICAL)
        toolbar.AddTool(1100, '', wx.Bitmap(store_path+ "png/tab_quant.png"))
        toolbar.AddSeparator()
        toolbar.AddTool(1101, '', wx.Bitmap(store_path+ "png/tab_trade.png"))
        toolbar.AddSeparator()
        toolbar.AddTool(1102, '', wx.Bitmap(store_path+ "png/tab_config.png"))
        toolbar.AddSeparator()
        toolbar.Realize()
        toolbar.Bind(wx.EVT_TOOL, self._ev_toolbar_trig)
        return toolbar

    def _ev_toolbar_trig(self, event):

        if event.GetId() == 1100:  # 量化按钮
            pass
        elif event.GetId() == 1101:  # 交易配置界面
            self.trade_frame = TradeFrame(parent=None, id=type,
                               displaySize=wx.DisplaySize(), Fun_SwFrame=self.fun_swframe)
            self.trade_frame.Centre()
            self.trade_frame.Show(True)

        elif event.GetId() == 1102:  # 系统配置界面
            self.conf_frame = ConfFrame(parent=None, id=type,
                              displaySize=wx.DisplaySize(), Fun_SwFrame=self.fun_swframe)
            self.conf_frame.Show(True)
        else:
            pass

    def _init_treelist_strategy(self, subpanel):

        # 创建一个 treeListCtrl object
        self.treeListStgy = CollegeTreeListCtrl(parent=subpanel, pos=(-1, 39), size=(250, 200))
        self.treeListStgy.Bind(wx.EVT_TREE_SEL_CHANGED, self._ev_click_on_treelist)

        return self.treeListStgy

    def _init_treelist_stock(self, subpanel):

        self.treeListStock = CollegeTreeListCtrl2(parent=subpanel, store_path=data_path, size=(200, 400))
        self.treeListStock.Bind(wx.EVT_TREE_SEL_CHANGED, self._ev_OnTreeListCtrlClickFunc)

        return self.treeListStock


    def _init_log_notebook(self):
        # 创建日志区面板
        self.LogNoteb = wx.Notebook(self)
        self.sys_log_tx = self._init_text_log(self.LogNoteb)
        self.patten_log_tx = self._init_text_log(self.LogNoteb)

        self.LogNoteb.AddPage(self.sys_log_tx, "系统日志")
        self.LogNoteb.AddPage(self.patten_log_tx, "选股日志")

        return self.LogNoteb

    def _init_nav_notebook(self):

        # 创建导航区面板
        self.NavNoteb = wx.Notebook(self)

        self.NavNoteb.AddPage(self._init_treelist_strategy(self.NavNoteb), "策略导航")
        self.NavNoteb.AddPage(self._init_treelist_stock(self.NavNoteb), "股票源索引")
        self.NavNoteb.AddPage(self._init_grid_pl(self.NavNoteb), "股票池索引")

        return self.NavNoteb

    def _init_para_notebook(self):

        # 创建参数区面板
        self.ParaNoteb = wx.Notebook(self)
        self.ParaStPanel = wx.Panel(self.ParaNoteb, -1) # 行情
        self.ParaBtPanel = wx.Panel(self.ParaNoteb, -1) # 回测 back test
        self.ParaPtPanel = wx.Panel(self.ParaNoteb, -1) # 选股流程 pick stock

        # 第二层布局
        self.ParaStPanel.SetSizer(self.add_stock_para_lay(self.ParaStPanel))
        self.ParaBtPanel.SetSizer(self.add_backt_para_lay(self.ParaBtPanel))
        self.ParaPtPanel.SetSizer(self.add_pick_para_lay(self.ParaPtPanel))

        self.ParaNoteb.AddPage(self.ParaStPanel, "择时参数")
        self.ParaNoteb.AddPage(self.ParaBtPanel, "回测参数")
        self.ParaNoteb.AddPage(self.ParaPtPanel, "选股流程")

        # 此处涉及windows和macos的区别
        sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "macos":
            self.ParaNoteb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._ev_change_noteb)
        else:
            self.ParaNoteb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._ev_change_noteb)

        return self.ParaNoteb

    def _init_status_bar(self):

        self.statusBar = self.CreateStatusBar() # 创建状态条
        # 将状态栏分割为3个区域,比例为2:1
        self.statusBar.SetFieldsCount(4)
        self.statusBar.SetStatusWidths([-2, -1, -1, -1])
        t = time.localtime(time.time())
        self.SetStatusText("公众号：元宵大师带你用Python量化交易", 0)
        self.SetStatusText("当前版本：%s" % Base_File_Oper.load_sys_para("sys_para.json")["__version__"], 1)
        self.SetStatusText("当前系统：%s" % Base_File_Oper.load_sys_para("sys_para.json")["operate_sys"], 2)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 3)

    def _init_menu_bar(self):

        regMenuInfter = {"&离线数据下载":{"&开始下载": self._ev_click_menu_start,
                                        '&刷新文件':self._ev_click_menu_fresh,
                                        '&补全下载':self._ev_click_menu_compt,
                                        '&停止下载': self._ev_click_menu_stop},
                         "&使用帮助": {"&报错排查": self._ev_err_guide_menu, '&功能说明': self._ev_funt_guide_menu},
                         "&股票池管理": {"&导入我的股票池": self._ev_import_code_menu, "&导出我的股票池": self._ev_export_code_menu},
                         "&主菜单": {"&返回": self._ev_switch_menu}}

        # 创建窗口面板
        menuBar = wx.MenuBar(style=wx.MB_DOCKABLE)

        if isinstance(regMenuInfter, dict):  # 使用isinstance检测数据类型
            for mainmenu, submenus in regMenuInfter.items():
                menuobj = wx.Menu()
                for submenu, funct in submenus.items():
                    subitem = wx.MenuItem(menuobj, wx.ID_ANY, submenu)
                    if funct != None:
                        self.Bind(wx.EVT_MENU, funct, subitem) # 绑定事件
                    menuobj.AppendSeparator()
                    menuobj.Append(subitem)
                menuBar.Append(menuobj, mainmenu)
            self.SetMenuBar(menuBar)

        # 以上代码遍历方式完成以下的内容
        """
        # 返回主菜单按钮
        mainmenu = wx.Menu() 
        backitem = wx.MenuItem(mainmenu, wx.ID_ANY, '&返回')
        self.Bind(wx.EVT_MENU, self._ev_switch_menu, backitem)  # 绑定事件
        mainmenu.Append(backitem)
        menuBar.Append(mainmenu, '&主菜单')
        self.SetMenuBar(menuBar)
        """

    def update_download_ochlv_result(self):

        self.syslog.clr_print()
        update_all_count = 0
        update_success_count = 0
        update_fail_count = 0
        self.failed_list.clear()
        self.elapsed_time = time.perf_counter()

        df_chg = pd.DataFrame()

        while not q_results.empty():
            info = q_results.get()

            #self.syslog.re_print("股票代码:{}; 更新状态:{}; 更新数目:{}".format(info["code"], info["status"], info["number"]))

            if info["status"] == "Success":
                update_success_count += 1
                update_all_count += 1

                # 以下在更新行情数据结束后更新RPS数据
                try:
                    st_name = self.code_table.get_name(info["code"])
                    df_chg.loc[:, st_name] = info["pct"]
                except Exception as e:
                    print(info["code"], e)

            elif info["status"] == "Fail":
                update_fail_count += 1
                #self.syslog.re_print('更新失败的股票为：{}\n'.format(info["code"]))
                self.failed_list.append(info["code"])

        Base_File_Oper.save_patten_analysis(df_chg, f"计算RPS使用的涨跌幅数据")
        self.syslog.re_print('*'*10)
        self.syslog.re_print('共更新{}支股票，{}支股票增加数据，{}支股票更新失败'.format(update_all_count, update_success_count, update_fail_count))
        self.syslog.re_print('共耗时{}秒'.format(self.elapsed_time - self.start_time))

    def switch_main_panel(self, org_panel=None, new_panel=None, inplace=True):

        if id(org_panel) != id(new_panel):

            self.vbox_sizer_b.Hide(org_panel)

            if inplace == True:
                self.vbox_sizer_b.Replace(org_panel, new_panel) # 等类型可替换
            else:
                # 先删除后添加
                self.vbox_sizer_b.Detach(org_panel)
                self.vbox_sizer_b.Add(new_panel, proportion=10, flag=wx.EXPAND | wx.BOTTOM, border=5)

            self.vbox_sizer_b.Show(new_panel)
            self.SetSizer(self.HBoxPanelSizer)
            self.HBoxPanelSizer.Layout()

    def _ev_change_noteb(self, event):

        #print(self.ParaNoteb.GetSelection())

        old = event.GetOldSelection()
        new = event.GetSelection()

        sw_obj = [[self.DispPanel, self.FlexGridSizer], self.BackMplPanel, self.grid_pk]

        if (old >= len(sw_obj)) or (new >= len(sw_obj)):
            raise ValueError(u"切换面板号出错！")

        org_panel = sw_obj[old]
        new_panel = sw_obj[new]

        if (old == 0):
            if self.pick_graph_last != 0:
                org_panel = self.FlexGridSizer
            else:
                org_panel = self.DispPanel

        if new == 0:
            if self.pick_graph_last != 0:
                new_panel = self.FlexGridSizer
            else:
                new_panel = self.DispPanel

        ex_flag = False

        if type(sw_obj[old]) == type(sw_obj[new]): ex_flag = True # 等类型可替换

        self.switch_main_panel(org_panel, new_panel, ex_flag)

    def add_stock_para_lay(self, sub_panel):

        # 择时参数
        stock_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 择时参数——输入股票代码
        self.stock_code_box = wx.StaticBox(sub_panel, -1, u'股票代码')
        self.stock_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stock_code_cbox = wx.ComboBox(sub_panel, -1, value="sz.000876",
                                           choices=['sh.000001', 'sz.399001', 'sz.399006'],
                                           style=wx.CB_DROPDOWN)
        self.stock_code_sizer.Add(self.stock_code_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 择时参数——多子图显示
        self.pick_graph_box = wx.StaticBox(sub_panel, -1, u'多子图显示')
        self.pick_graph_sizer = wx.StaticBoxSizer(self.pick_graph_box, wx.VERTICAL)
        self.pick_graph_cbox = wx.ComboBox(sub_panel, -1, u"未开启",
                                           choices=[u"未开启", u"A股票走势-MPL", u"B股票走势-MPL", u"A股票走势-WEB", u"B股票走势-WEB"],
                                           style=wx.CB_READONLY | wx.CB_DROPDOWN)
        self.pick_graph_cbox.SetSelection(0)
        self.pick_graph_last = self.pick_graph_cbox.GetSelection()
        self.pick_graph_sizer.Add(self.pick_graph_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_graph_cbox.Bind(wx.EVT_COMBOBOX, self._ev_select_graph)

        # 择时参数——股票组合分析
        self.group_analy_box = wx.StaticBox(sub_panel, -1, u'投资组合分析')
        self.group_analy_sizer = wx.StaticBoxSizer(self.group_analy_box, wx.VERTICAL)
        self.group_analy_cmbo = wx.ComboBox(sub_panel, -1, u"预留A",
                                             choices=[u"预留A", u"收益率/波动率", u"走势叠加分析", u"财务指标评分-预留"],
                                             style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 策略名称
        self.group_analy_sizer.Add(self.group_analy_cmbo, proportion=0,
                                    flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.group_analy_cmbo.Bind(wx.EVT_COMBOBOX, self._ev_group_analy)  # 绑定ComboBox事件

        # 下载按钮
        self.adv_func_but = wx.Button(sub_panel, -1, "高级功能")
        self.adv_func_but.Bind(wx.EVT_BUTTON, self._ev_adv_func)  # 绑定按钮事件

        stock_para_sizer.Add(self.stock_code_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.pick_graph_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.group_analy_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.adv_func_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return stock_para_sizer

    def add_backt_para_lay(self, sub_panel):

        # 回测参数
        back_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 行情参数——输入股票代码
        self.backt_code_box = wx.StaticBox(sub_panel, -1, u'股票代码')
        self.backt_code_sizer = wx.StaticBoxSizer(self.backt_code_box, wx.VERTICAL)
        self.backt_code_input = wx.TextCtrl(sub_panel, -1, "sz.000876", style=wx.TE_PROCESS_ENTER)
        self.backt_code_sizer.Add(self.backt_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 回测按钮
        self.start_back_but = wx.Button(sub_panel, -1, "开始回测")
        self.start_back_but.Bind(wx.EVT_BUTTON, self._ev_start_run)  # 绑定按钮事件

        # 交易日志
        self.trade_log_but = wx.Button(sub_panel, -1, "交易日志")
        self.trade_log_but.Bind(wx.EVT_BUTTON, self._ev_trade_log)  # 绑定按钮事件

        back_para_sizer.Add(self.backt_code_sizer, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        back_para_sizer.Add(self.start_back_but, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        back_para_sizer.Add(self.trade_log_but, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        return back_para_sizer

    def add_pick_para_lay(self, sub_panel):

        # 选股参数
        pick_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 子参数——剔除ST/*ST 及 标记自选股
        self.adv_select_box = wx.StaticBox(sub_panel, -1, u'勾选确认')
        self.adv_select_sizer = wx.StaticBoxSizer(self.adv_select_box, wx.HORIZONTAL)
        self.mark_self_chk = wx.CheckBox(sub_panel, label='标记自选股')
        self.mark_self_chk.Bind(wx.EVT_CHECKBOX, self._ev_mark_self)  # 绑定复选框事件
        self.adv_select_sizer.Add(self.mark_self_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 爬虫接口获取目前支持以下几类
        self.crawer_backend = {u"爬虫每日指标": DailyIndImp,
                               u"爬虫北向资金": NorthMoneyImp,
                               u"爬虫每日涨停": UpLimitImp}

        # 选股序列按钮——刷新数据 + 开始选股 + 保存结果
        self.data_drive_but = wx.Button(sub_panel, -1, "开始数据驱动选股")
        self.data_drive_but.Bind(wx.EVT_BUTTON, self._ev_dat_select_func)  # 绑定按钮事件

        self.patten_drive_but = wx.Button(sub_panel, -1, "开始形态驱动选股")
        self.patten_drive_but.Bind(wx.EVT_BUTTON, self._ev_patten_select_func)  # 绑定按钮事件

        self.rps_drive_but = wx.Button(sub_panel, -1, "开始RPS排名选股")
        self.rps_drive_but.Bind(wx.EVT_BUTTON, self._ev_rps_select_func)  # 绑定按钮事件

        self.back_test_but = wx.Button(sub_panel, -1, "开始选股结果回测")
        self.back_test_but.Bind(wx.EVT_BUTTON, self._ev_backtest_select_func)  # 绑定按钮事件

        pick_para_sizer.Add(self.adv_select_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.data_drive_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.patten_drive_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.rps_drive_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.back_test_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return pick_para_sizer

    def _init_grid_pk(self):# 创建wxGrid表格对象
        # 初始化选股表格
        self.grid_pk = GridTable(parent=self)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_cell_lclick_pkcode, self.grid_pk)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self._ev_label_lclick_pkcode, self.grid_pk)

        self.df_use = pd.DataFrame()
        self.filte_result = pd.DataFrame()
        return self.grid_pk

    def _init_grid_pl(self, subpanel):
        # 初始化股票池表格
        self.grid_pl = GridTable(parent=subpanel, nrow=0, ncol=2)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_click_plcode, self.grid_pl)
        return self.grid_pl

    def _init_listbox_mult(self):

        self.mult_analyse_box = wx.StaticBox(self, -1, u'组合分析股票池')
        self.mult_analyse_sizer = wx.StaticBoxSizer(self.mult_analyse_box, wx.VERTICAL)
        self.listBox = wx.ListBox(self, -1, size=(self.M1_width, self.M1S2_length), choices=[], style=wx.LB_EXTENDED)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self._ev_list_select)
        self.mult_analyse_sizer.Add(self.listBox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        return self.mult_analyse_sizer

    def _init_gauge_bar(self):

        self.gauge_count = 0

        self.gauge_indicate_box = wx.StaticBox(self, -1, u'执行进度显示')
        self.gauge_indicate_sizer = wx.StaticBoxSizer(self.gauge_indicate_box, wx.VERTICAL)

        self.gaugeBar = wx.Gauge(self, -1, range=100)
        self.gaugeBar.SetValue(self.gauge_count)

        self.gauge_indicate_sizer.Add(self.gaugeBar, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        return self.gauge_indicate_sizer

    def _init_text_log(self, subpanel):

        # 创建并初始化系统日志框
        temp_log_tx = wx.TextCtrl(subpanel, style=wx.TE_MULTILINE, size=(self.M1_width, self.M1S1_length))
        temp_log_tx.SetMaxLength(0)
        return temp_log_tx

    def refresh_grid(self, df, back_col=""):
        self.grid_pk.SetTable(df, self.tran_col)
        self.grid_pk.SetSelectCol(back_col)

    def refresh_grid1(self, update_df):

        self.grid.Destroy()  # 先摧毁 后创建
        self.data_to_grid(update_df)

        self.HBoxPanelSizer.Add(self.grid, proportion=10, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.HBoxPanelSizer.Layout()

    def _ev_select_graph(self, event):

        item = event.GetSelection()

        # 显示区一级切换
        if item != 0 and self.pick_graph_last == 0: # 单图切到多子图

            if item <= 2: # 1-2 属于MPL显示区
                self.graphs_obj = SubGraphs(self)
            elif item <= 4: # 3-4 属于WEB显示区
                self.graphs_obj = WebGraphs(self)
            else: # 故障保护
                MessageDialog("一级切换-0错误！", u"错误警告")
                self.graphs_obj = SubGraphs(self)
            self.switch_main_panel(self.DispPanel, self.graphs_obj.FlexGridSizer, False)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item == 0 and self.pick_graph_last != 0: # 多子图切到单图
            #print(self.vbox_sizer_b.GetItem(self.DispPanel))
            self.switch_main_panel(self.FlexGridSizer, self.DispPanel, False)

        elif item <= 2 and self.pick_graph_last > 2:
            self.graphs_obj = SubGraphs(self)
            self.switch_main_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item > 2 and self.pick_graph_last <= 2:
            self.graphs_obj = WebGraphs(self)
            self.switch_main_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer
        else:
            pass

        # 显示区二级切换
        if item == 1 or item == 3:
            self.DispPanelA = self.graphs_obj.DispPanel0
            #self.ochl = self.DispPanel0.ochl
            #self.vol = self.DispPanel0.vol
        elif item == 2 or item == 4:
            self.DispPanelA = self.graphs_obj.DispPanel1
            #self.ochl = self.DispPanel1.ochl
            #self.vol = self.DispPanel1.vol
        else:
            self.DispPanelA = self.DispPanel

        self.pick_graph_last = item

    def _ev_dat_select_func(self, event):

        select_msg = ChoiceDialog(u"选股流程点击处理事件", [u"第一步:刷新选股数据",
                                                  u"第二步:开始条件选股",
                                                  u"第三步:保存选股结果"])
        if select_msg == u"第一步:刷新选股数据":
            self._download_st_data()

        elif select_msg == u"第二步:开始条件选股":
            self._start_st_slect()

        elif select_msg == u"第三步:保存选股结果":
            self._save_st_result("保存条件筛选后的股票",
                                 dict(zip(self.df_use["股票名称"].values, self.df_use["股票代码"].values)))
        else:
            pass

    def _start_st_slect(self):

        if self.df_use.empty == True:
            MessageDialog("请先获取选股数据！", u"错误警告")
            return

        if self.mark_self_chk.GetValue() == True:  # 复选框被选中
            MessageDialog("先取消复选框！！！",  u"错误警告")
            return

        cond_dialog = CondSelDialog(self, "条件选股参数配置", self.filter)
        cond_dialog.Centre()

        # 第一步:收集控件中设置的选项
        if cond_dialog.ShowModal() != wx.ID_OK:
            return
        else:
            cond_paras = cond_dialog.feedback_paras()

            self.df_use.dropna(subset=['股票名称'], inplace=True)
            if cond_paras[u"剔除ST"] == True:  # 剔除ST/*ST
                self.df_use = self.df_use[self.df_use['股票名称'].apply(lambda x: x.find('ST') < 0)]

            if cond_paras[u"剔除科创板"] == True:  # 剔除科创板
                self.df_use = self.df_use[self.df_use['股票代码'].apply(lambda x: x.find('688') < 0)]

            val = cond_paras[u"条件选项"]

            if val in self.df_use.columns.tolist():  # DataFrame中是否存在指标

                if ("行业" in val) and (cond_paras[u"条件符号"] == u"等于"):

                    para_value = str(cond_paras[u"条件值"])

                    if para_value == "":
                        for value in list(set(self.df_use[val].values.tolist())):
                            self.filte_result = pd.concat([self.filte_result, self.df_use[self.df_use[val] == value]])
                    elif "|" in para_value:
                        for value in para_value.split("|"):  # 支持用"｜"符号查询多个
                            self.filte_result = pd.concat([self.filte_result, self.df_use[self.df_use[val] == value]])
                    else:
                        self.filte_result = self.df_use[self.df_use[val] == para_value]

                elif val in [u"股票代码", u"股票名称"]:
                    # 字符串type
                    para_values = str(cond_paras[u"条件值"])

                    if cond_paras[u"条件符号"] == u"等于":
                        for value in para_values.split("|"):  # 支持用"｜"符号查询多个
                            self.filte_result = pd.concat([self.filte_result, self.df_use[self.df_use[val] == value]])
                    else:
                        MessageDialog("【%s】选项只支持【等于】条件判断！！！" % (val), u"错误警告")
                        return

                else:

                    para_value = cond_paras[u"条件值"]

                    if cond_paras[u"条件符号"] == u"大于":
                        self.filte_result = self.df_use[self.df_use[val] > float(para_value)]
                    elif cond_paras[u"条件符号"] == u"小于":
                        self.filte_result = self.df_use[self.df_use[val] < float(para_value)]
                    elif cond_paras[u"条件符号"] == u"等于":
                        self.filte_result = self.df_use[self.df_use[val] == para_value]
                    else:
                        pass

                    if cond_paras[u"结果排序"] == u"降序":
                        self.filte_result.sort_values(by=val, axis='index', ascending=False, inplace=True,
                                                      na_position='last')
                    elif cond_paras[u"结果排序"] == u"升序":
                        self.filte_result.sort_values(by=val, axis='index', ascending=True, inplace=True,
                                                      na_position='last')
                    else:
                        pass

                if self.filte_result.empty != True:

                    ser_col = self.filte_result[val]  # 先单独保存
                    self.filte_result.drop(val, axis=1, inplace=True)  # 而后从原数据中删除
                    self.filte_result.insert(0, val, ser_col)  # 插入至首个位置

                    self.df_use = self.filte_result
                    self.filte_result = pd.DataFrame()
                    self.refresh_grid(self.df_use, val)

                else:
                    MessageDialog("未找到符合条件的数据！！！", u"错误警告")

    def _download_st_data(self): # 复位选股按钮事件

        if self.mark_self_chk.GetValue() == True: # 复选框被选中
            MessageDialog("先取消复选框！！！")
            return

        date_dialog = DateInputDialog(self, "输入选股日期")

        date_dialog.Centre()
        # 第一步:收集控件中设置的选项
        if date_dialog.ShowModal() != wx.ID_OK:
            return
        else:
            sdate_obj = date_dialog.feedback_paras()
            sdate_val = datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)

            select_src = ChoiceDialog(u"选股数据源选取", list(self.crawer_backend.keys())+
                                                        [u"基金季度持仓",
                                                         u"调用同花顺问财",
                                                         u"离线自定义数据(导入即用)"])

            if (select_src == "爬虫每日指标") or (select_src == "爬虫北向资金") or (select_src == "爬虫每日涨停"):
                self.ts_data = self.crawer_backend.get(select_src)(self.syslog) # 另一种方式 self.crawer_backend[select_src](self.syslog)
                self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y%m%d'))  # 刷新self.df_join

            elif select_src == "基金季度持仓":
                self.df_join = ReadFundDatFromSql(self.syslog, sdate_val)

            elif select_src == "调用同花顺问财":
                cond_dialog = MsgInputDialog(self, "输入选股条件")

                cond_dialog.Centre()
                # 第一步:收集控件中设置的选项
                if cond_dialog.ShowModal() != wx.ID_OK:
                    return

                self.ths_if = THSAskFinanceIf(self.syslog)
                self.df_join = self.ths_if.get_wencai_data(
                    sdate_val.strftime('%Y%m%d'),
                    cond_dialog.feedback_paras()[0],
                    cond_dialog.feedback_paras()[1])
                # print(self.df_join)

            elif select_src == u"离线自定义数据(导入即用)":
                # 离线csv文件
                # 第一步:收集导入文件路径
                get_path = ImportFileDiag(pickout_path)

                if get_path != '':
                    # 组合加入tushare数据
                    self.ts_data = Csv_Backend(select_src)
                    self.df_join = self.ts_data.load_pick_data(get_path)
            else:
                return

            if self.df_join.empty == True:
                MessageDialog("选股数据为空！请检查选股日期是否有效交易日或爬虫数据源是否已经失效！\n", u"错误警告")
            else:
                # 数据获取正常后执行

                self.filter = self.df_join.columns.tolist()
                self.tran_col = dict(zip(self.df_join.columns.tolist(), self.filter))

                if select_src == "爬虫每日指标":

                    dlg_mesg = wx.SingleChoiceDialog(None, "刷新股票池 或者 刷新数据源？",
                                                     u"刷新类别选择", ['A股数据源', '自选股票池'])
                    dlg_mesg.SetSelection(0)  # default selection

                    if dlg_mesg.ShowModal() == wx.ID_OK:
                        message = dlg_mesg.GetStringSelection()
                        dlg_mesg.Destroy()
                        if message == '自选股票池':
                            df_pool = pd.DataFrame()
                            for sub_dict in self.self_pool.load_pool_stock().values():
                                code = self.code_table.conv_ts_code(sub_dict)
                                df_pool = df_pool.append(self.df_join[self.df_join["股票代码"] == code],
                                                                   ignore_index=True)
                            self.df_join = df_pool

                self.df_use = self.df_join
                self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

                if select_src == "爬虫每日指标":

                    if MessageDialog('是否查看Web版【板块-个股-涨跌幅】集合', u"温馨提示") == "点击Yes":
                        #try:
                        bk_to_pct = self.df_join.groupby(u'所属行业')[u'涨跌幅'].mean()
                        st_to_pct = self.df_join.groupby([u'所属行业', u'股票名称'])[u'涨跌幅'].mean()

                        bk_treemap = []

                        for bk_name, bk_pct in bk_to_pct.items():
                            child_treemap = []

                            for st_name, st_pct in st_to_pct[bk_name].items():
                                child_treemap.append({"value": round(st_pct, 2), "name": st_name})

                            bk_treemap.append({"value": round(bk_pct, 2), "name": bk_name, "children": child_treemap})

                        Pyechart_Drive.TreeMap_Handle(bk_treemap, "所属行业-个股-涨幅%", "行业板块")

                        web_disp = WebDialog(self, "", "treemap_base.html")
                        web_disp.Centre()
                        if web_disp.ShowModal() == wx.ID_OK:
                            pass
                        #except:
                        #    MessageDialog("html文件加载出错，可前往文件夹点击查看！")

                elif select_src == "爬虫每日涨停":

                    if MessageDialog('是否查看【板块内涨停个股数量】', u"温馨提示") == "点击Yes":

                        ser_count = self.df_use["所属行业"].value_counts()
                        industry_count_draw = IndustryCountDialog(self, u"统计行业板块涨停板个股数量", "行业板块",
                                                                  pd.DataFrame(ser_count.values,
                                                                               index=ser_count.index,
                                                                               columns=["涨停股数量"]))
                        industry_count_draw.Centre()
                        if industry_count_draw.ShowModal() == wx.ID_OK:
                            pass

                    if MessageDialog('是否查看【涨停个股题材原因类别统计】', u"温馨提示") == "点击Yes":

                        count_reasons = []
                        for reason in self.df_use["涨停原因类别"].tolist():
                            if reason is not np.NAN:
                                count_reasons.extend(reason.split("+"))

                        reason_name = []
                        reason_count = []

                        for reason in set(count_reasons): # count_reasons内容是count_reasons的无重复
                            reason_name.append(reason)
                            reason_count.append(count_reasons.count(reason))

                        reason_count_df = pd.DataFrame(reason_count, index=reason_name, columns=["涨停股原因"])
                        reason_count_df.sort_values(by=['涨停股原因'], ascending=False, inplace=True)
                        reason_count_draw = IndustryCountDialog(self, u"统计涨停个股题材原因类别", "概念题材", reason_count_df.head(20))
                        reason_count_draw.Centre()
                        if reason_count_draw.ShowModal() == wx.ID_OK:
                            pass

    def _save_st_result(self, dialog_cont:str, st_name_code:dict):
        # 保存选股按钮事件

        choice_msg = ChoiceDialog(dialog_cont, [u"完全替换", u"增量更新"])

        if choice_msg == u"完全替换":
            self.self_pool.update_replace_st(st_name_code)
        elif choice_msg == u"增量更新":
            self.self_pool.update_increase_st("股票", st_name_code)
        else:
            return
        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])
        #self.df_use.to_csv('table-stock.csv', columns=self.df_use.columns, index=True, encoding='GB18030')

    def _ev_mark_self(self, event):
        # 标记自选股事件

        if self.df_use.empty == True:
            MessageDialog("无选股数据！", "错误警告")
        else:
            self.df_use.reset_index(drop=True, inplace=True) # 重排索引

            if self.mark_self_chk.GetValue() == True: # 复选框被选中

                for code in list(self.self_pool.load_pool_stock().values()): # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 0, wx.YELLOW)
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 1, wx.YELLOW)
            else:
                for code in list(self.self_pool.load_pool_stock().values()): # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 0, wx.WHITE)
                        self.grid_pk.SetCellBackgroundColour(n_list[0], 1, wx.WHITE)
            self.grid_pk.Refresh()

    def _ev_trade_log(self, event):

        user_trade_log = UserDialog(self, title=u"回测提示信息", label=u"交易详细日志")

        """ 自定义提示框 """
        if user_trade_log.ShowModal() == wx.ID_OK:
            pass
        else:
            pass

    def _ev_click_on_treelist(self, event):

        self.curTreeItem = self.treeListStgy.GetItemText(event.GetItem())

        if self.curTreeItem != None:
            # 当前选中的TreeItemId对象操作

            if MessageDialog('当前点击:{0}!'.format(self.curTreeItem), u"温馨提示")!= "点击Yes":
                return
            for m_key, m_val in self.treeListStgy.colleges.items():
                for s_key in m_val:
                    if s_key.get('名称', '') == self.curTreeItem:
                        if s_key.get('函数', '') != "未定义":
                            if (m_key == u"衍生指标") or (m_key == u"K线形态"):
                                # 第一步:收集控件中设置的选项
                                st_label = s_key['标识']
                                ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
                                ochl_paras.Centre()
                                # 第一步:收集控件中设置的选项
                                if ochl_paras.ShowModal() != wx.ID_OK:
                                    return
                                else:
                                    st_paras = ochl_paras.feedback_paras()

                                choice_msg = ChoiceDialog("择时策略作用范围", [u"指定个股", u"自选股票池"])

                                if choice_msg == u"指定个股":
                                    st_code = self.stock_code_cbox.GetValue()
                                    st_name = self.code_table.get_name(st_code)

                                    self.stock_dat = self.requset_stock_dat(st_code, st_name,
                                                                            st_paras["股票周期"], st_paras["股票复权"],
                                                                            st_paras["开始日期"], st_paras["结束日期"])

                                    # 第二步:获取股票数据-使用self.stock_dat存储数据
                                    if self.stock_dat.empty == True:
                                        MessageDialog("获取股票数据出错！\n")
                                    else:
                                        # 第三步:绘制可视化图形
                                        if self.pick_graph_cbox.GetSelection() != 0:
                                            self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                                            self.DispPanelA.draw_subgraph(self.stock_dat, st_code,
                                                                          st_paras["股票周期"] + st_paras["股票复权"])
                                        else:
                                            # 配置图表属性
                                            firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                                         st_code=st_code,
                                                                         st_name=st_name,
                                                                         st_period=st_paras["股票周期"],
                                                                         st_auth=st_paras["股票复权"],
                                                                         st_label=st_label)

                                            self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)
                                        self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图

                                elif choice_msg == u"自选股票池":
                                    user_trade_log = ScanDialog(self, st_label, self.self_pool.load_pool_stock(),
                                                                 st_paras["股票周期"], st_paras["股票复权"],
                                                                 st_paras["开始日期"], st_paras["结束日期"],
                                                                 title=u"扫描自选股票池择时信号")
                                    user_trade_log.Centre()
                                    #user_trade_log.Show()
                                    if user_trade_log.ShowModal() != wx.ID_OK:
                                        return
                                    else:
                                        trade_paras = {}
                                        for code, paras in user_trade_log.back_results().items():
                                            name = self.code_table.get_name(code)
                                            trade_paras = {name: {}}
                                            trade_paras[name] = paras
                                        self.trade_pool.update_increase_st(trade_paras)
                                else:
                                    return
                            else:
                                self.function = getattr(Base_Strategy_Group, s_key.get('define', ''))
                        else:
                            MessageDialog("该接口未定义！")
                        break

    ################################### 事件函数 ###################################
    def _ev_OnTreeListCtrlClickFunc(self, event):
        self.currentTreeItem = self.treeListStock.GetItemText(event.GetItem())

        try:
            df = pd.read_csv(data_path + self.currentTreeItem, index_col=0, parse_dates=[u"日期"], encoding='GBK',
                             engine='python')  # 文件名中含有中文时使用engine为python
            view_stock_data = ViewGripDiag(self, u"查看离线日线数据csv", df)
            """ 自定义提示框 """
            if view_stock_data.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        except:
            MessageDialog("读取文件出错! \n")

    def _ev_start_run(self, event): # 点击运行回测

        # 第一步:收集控件中设置的选项
        st_code = self.backt_code_input.GetValue()
        st_name = self.code_table.get_name(st_code)
        backt_paras = BacktGraphDialog(self, "回测参数配置")
        backt_paras.Centre()
        # 第一步:收集控件中设置的选项
        if backt_paras.ShowModal() != wx.ID_OK:
            return
        else:
            bt_paras = backt_paras.feedback_paras()


        # 第二步:获取股票数据-依赖行情界面获取的数据
        self.backt_dat = self.requset_stock_dat(st_code,  st_name,
                                                bt_paras["股票周期"], bt_paras["股票复权"],
                                                bt_paras["开始日期"], bt_paras["结束日期"])

        if self.backt_dat.empty == True:
            MessageDialog("获取回测数据出错！\n")
            return

        if self.function == '':
            MessageDialog("未选择回测策略！")
            return

        # 第三步:绘制可视化图形
        # 配置图表属性
        back_para = self.call_method(self.event_task['cfg_back_para'],
                                     st_code=st_code,
                                     cash_value=bt_paras[u"初始资金"],
                                     stake_value=bt_paras[u"交易规模"],
                                     slippage_value=bt_paras[u"滑点"],
                                     commission_value=bt_paras[u"手续费"],
                                     tax_value=bt_paras[u"印花税"])

        self.BackMplPanel.back_graph_run(self.function(self.backt_dat), **back_para)
        # 修改图形的任何属性后都必须更新GUI界面
        self.BackMplPanel.update_subgraph()

    def requset_stock_dat(self, st_code, st_name, st_period, st_auth, sdate_obj, edate_obj):

        # 第二步:获取股票数据-调用sub event handle
        stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                          st_code=st_code,
                                          st_period=st_period,
                                          st_auth=st_auth,
                                          sdate_obj=sdate_obj,
                                          edate_obj=edate_obj)
        return stock_dat

    def handle_active_code(self, st_code, st_name, items=[u"添加自选股票池", u"从股票池中剔除",
                                                        u"加入组合分析池", u"查看现金流量",
                                                        u"查看行情走势", u"查看F10资料",
                                                        u"K线自动播放", u"个股RPS跟踪",
                                                        u"导入离线数据"]): # 点击股票代码后处理模块

        select_msg = ChoiceDialog(u"自选股点击处理事件", items)
        st_code = self.code_table.conv_ts_code(st_code) # 先统一转换为xxxxxx.SH/SZ 格式

        if select_msg == u"查看行情走势":

            self.ParaNoteb.SetSelection(0)

            ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
            ochl_paras.Centre()
            # 第一步:收集控件中设置的选项
            if ochl_paras.ShowModal() != wx.ID_OK:
                return
            else:
                st_paras = ochl_paras.feedback_paras()

            self.stock_dat = self.requset_stock_dat(st_code,  st_name,
                                                    st_paras["股票周期"], st_paras["股票复权"],
                                                    st_paras["开始日期"], st_paras["结束日期"])

            if self.stock_dat.empty == True:
                MessageDialog("获取股票数据出错！\n")
            else:

                if len(self.stock_dat) >= 356:
                    MessageDialog("获取股票数据量较大！默认显示最近的365个BAR数据！\n", u"温馨提示")
                    self.stock_dat = self.stock_dat[-356:]

                # 第三步:绘制可视化图形
                if self.pick_graph_cbox.GetSelection() != 0:
                    self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                    self.DispPanelA.draw_subgraph(self.stock_dat, st_code, st_paras["股票周期"] + st_paras["股票复权"])

                else:
                    # 配置图表属性
                    firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                 st_code=st_code,
                                                 st_name=st_name,
                                                 st_period=st_paras["股票周期"],
                                                 st_auth=st_paras["股票复权"])

                    self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)

                self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图

        elif select_msg == u"加入组合分析池":
            self._add_analyse_list(st_code+"|"+st_name)
            self.self_pool.update_increase_st("组合", {st_name: st_code})

        elif select_msg == u"查看现金流量":

            text = self.call_method(self.event_task['get_cash_flow'], st_code=st_code)

            if MessageDialog(
                    text + "\n添加股票[%s]到自选股票池？" % (st_code + "|" + st_name)) == "点击Yes":
                # self._add_analyse_list(self.code_table.conv_code(st_code) + "|" + st_name)
                # 自选股票池 更新股票
                self.self_pool.update_increase_st("股票", {st_name: st_code})
                self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        elif select_msg == u"添加自选股票池":
            self.self_pool.update_increase_st("股票", {st_name: st_code})
            self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        elif select_msg == u"从股票池中剔除":
            self.self_pool.delete_one_st(st_name)
            self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

        elif select_msg == u"查看F10资料":
            dialog = BrowserF10(self, u"个股F10资料", st_code)
            dialog.Show()

        elif select_msg == u"K线自动播放":

            self.ParaNoteb.SetSelection(0)
            ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
            ochl_paras.Centre()
            # 第一步:收集控件中设置的选项
            if ochl_paras.ShowModal() != wx.ID_OK:
                return
            else:
                st_paras = ochl_paras.feedback_paras()

            self.stock_dat = self.requset_stock_dat(st_code, st_name,
                                                    st_paras["股票周期"], st_paras["股票复权"],
                                                    st_paras["开始日期"], st_paras["结束日期"])

            dialog = KlineRunDialog(self, u"K线自动播放", self.stock_dat)
            dialog.Show()

        elif select_msg == u"导入离线数据":

            self.ParaNoteb.SetSelection(0)

            if MessageDialog("请手动填写[股票名称][股票周期][股票复权]！\n该内容与图表标签相关！\n点击Yes继续；点击No去配置", u"温馨提示") == "点击No":
                return

            # 第一步:收集导入文件路径/名称/周期/起始时间
            get_path = ImportFileDiag(data_path)
            st_code = self.stock_code_cbox.GetValue()
            st_name = self.code_table.get_name(st_code)

            ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
            ochl_paras.Centre()
            # 第一步:收集控件中设置的选项
            if ochl_paras.ShowModal() != wx.ID_OK:
                return
            else:
                st_paras = ochl_paras.feedback_paras()

            # 第二步:加载csv文件中的数据
            if get_path != '':
                self.stock_dat = self.call_method(self.event_task['get_csvst_dat'],
                                                  get_path=get_path,
                                                  sdate_obj=st_paras["开始日期"], edate_obj=st_paras["结束日期"],
                                                  st_auth=st_paras["股票复权"], st_period=st_paras["股票周期"])

                if self.stock_dat.empty == True:
                    MessageDialog("文件内容为空！\n")
                else:

                    # 第三步:绘制可视化图形
                    if self.pick_graph_cbox.GetSelection() != 0:
                        self.DispPanelA.clear_subgraph()  # 必须清理图形才能显示下一幅图
                        self.DispPanelA.draw_subgraph(self.stock_dat, "csv导入" + st_code, st_name)
                    else:
                        # 配置图表属性
                        firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                     st_code="csv导入" + st_code,
                                                     st_name=st_name,
                                                     st_period=st_paras["股票周期"],
                                                     st_auth="不复权")
                        self.DispPanelA.firm_graph_run(self.stock_dat, **firm_para)
                    self.DispPanelA.update_subgraph()  # 必须刷新才能显示下一幅图

        elif select_msg == u"个股RPS跟踪":

            # 第一步: 收集控件中设置的选项
            patten_paras = SelectModeDialog(self, "个股RPS跟踪参数配置")

            patten_paras.Centre()
            # 第一步:收集控件中设置的选项
            if patten_paras.ShowModal() != wx.ID_OK:
                return
            else:
                pat_paras = patten_paras.feedback_paras()

            # 第一步:收集控件中设置的选项
            st_period = pat_paras["股票周期"]
            st_auth = pat_paras["股票复权"]

            # MessageDialog("为解决全市场股票扫描时的效率问题，日线周期默认使用本地股票数据！", "温馨提示")
            self.patlog.clr_print()
            self.patlog.re_print(f"启动{select_msg} 选股模型分析......\n")

            self.LogNoteb.SetSelection(1)

            df_search = Base_File_Oper.load_patten_analysis(f"计算RPS使用的涨跌幅数据")  # 构建一个dataframe用来装涨跌幅数据
            df_search = df_search.reindex(columns=df_search.columns)
            df_search.dropna(how='all', axis=1, inplace=True)
            df_search = df_search.fillna(0)
            df_search = df_search.rolling(window=pat_paras["选取涨跌幅滚动周期"]).mean().round(2)

            if len(df_search) > pat_paras["选取涨跌幅滚动周期"]:
                df_search = df_search[-(len(df_search) - pat_paras["选取涨跌幅滚动周期"]):].fillna(0)
            else:
                MessageDialog(f"选取涨跌幅滚动周期({pat_paras['选取涨跌幅滚动周期']}) 大于行情数据量！", "温馨提示")

            sym, num = st_code.split(".")

            track_name = self.code_table.get_name(st_code)

            df_track = Base_Indicate_Group.rps_stock_track(df_search, track_name)

            if (st_code.find('.') != -1) and track_name != "":  # 输入代码正常

                sdate_val = df_track.index[0]
                edate_val = df_track.index[-1]

                stock_dat = Csv_Backend.load_history_st_data(data_path + sym + num + '.csv',
                                                             sdate_val, edate_val, st_auth, st_period)

                self.patlog.re_print(f"\n开始跟踪个股{st_code}排名动态!")
                df_track["close"] = stock_dat.loc[sdate_val:edate_val, "收盘价"]

                # 第三步:绘制可视化图形
                rps_track_draw = RpsTrackDialog(self, u"个股收盘价走势 vs RPS排名", track_name, df_track)
                """ 自定义提示框 """
                if rps_track_draw.ShowModal() == wx.ID_OK:

                    # 保存图片到本地
                    plt.savefig(
                        os.path.dirname(os.path.dirname(__file__)) + '/ConfigFiles/' + f'跟踪{track_name}的RPS.jpg')
                    self.patlog.re_print(f"\n跟踪{track_name}动态RPS完成!已保存至ConfigFiles目录下")

        else:
            pass

    def _ev_click_plcode(self, event):  # 点击股票池股票代码

        # 收集股票池中名称和代码
        st_code = self.grid_pl.GetCellValue(event.GetRow(), 1)
        st_name = self.grid_pl.GetCellValue(event.GetRow(), 0)

        self.handle_active_code(st_code, st_name, [u"从股票池中剔除",
                                                    u"加入组合分析池",
                                                    u"查看现金流量",
                                                    u"查看行情走势",
                                                    u"查看F10资料",
                                                    u"K线自动播放"])

    def _ev_label_lclick_pkcode(self, event):

        # 收集表格中的列名
        col_label = self.grid_pk.GetColLabelValue(event.GetCol())

        if col_label == "所属行业" and self.src_dat_cmbo.GetStringSelection() == "离线财务报告":

            if MessageDialog("是否对比个股业绩报告？建议同行业板块对比！", u"温馨提示") == "点击Yes":

                if self.df_use.empty != True:

                    self.df_use.dropna(how='all', axis=1, inplace=True)
                    self.df_use.fillna(0, inplace = True)
                    self.df_use = self.df_use.assign(总分 = 0)

                    for col, series in self.df_use.iteritems():

                        if series.dtype == float and col != "总分":
                            self.df_use[col] = (series - series.mean())/series.var()
                            self.df_use.loc[:,"总分"] += self.df_use[col]

                    self.df_use.sort_values(by=["总分"], axis='index', ascending=False, inplace=True,
                                              na_position='last') # 降序

                    text = "对比后排名前五名单如下:\n"
                    updat_dict = {}
                    for name, code in zip(self.df_use["股票名称"][0:5], self.df_use["股票代码"][0:5]):
                        code = code[1:-1]
                        text += name + "|" + code + "\n"
                        updat_dict.update({name: self.code_table.conv_ts_code(code)})

                    if MessageDialog(text+"\n添加股票到自选股票池？") == "点击Yes":
                        # 自选股票池 更新股票
                        self.self_pool.update_increase_st("股票", updat_dict)
                        self.grid_pl.SetTable(self.self_pool.load_self_pool(), ["自选股", "代码"])

    def _ev_cell_lclick_pkcode(self, event):  # 点击选股表中股票代码

        # 收集表格中的列名
        col_label = self.grid_pk.GetColLabelValue(event.GetCol())

        if col_label == "股票代码":
            # 收集表格中的单元格
            try:
                st_code = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_name = self.code_table.get_name(st_code)
            except:
                MessageDialog("股票代码不在存储表中！检查是否为新股/退市等情况！")

        elif (col_label == "股票名称") or (("第" in col_label) and ("名" in col_label)):
            # 收集表格中的单元格
            try:
                st_name = self.grid_pk.GetCellValue(event.GetRow(), event.GetCol())
                st_code = self.code_table.get_code(st_name)
            except:
                MessageDialog("股票名称不在存储表中！检查是否为新股/退市等情况！")

        else:
            MessageDialog("请点击股票代码或股票名称！")
            return

        adv_func_list = [u"添加自选股票池", u"加入组合分析池", u"查看现金流量",
                         u"查看行情走势", u"查看F10资料", u"K线自动播放", u"个股RPS跟踪"]

        self.handle_active_code(st_code, st_name, adv_func_list)

    def _ev_list_select(self, event): # 双击从列表中剔除股票

        # 等价与GetSelection() and indexSelected
        if MessageDialog("是否从组合分析股票池中删除该股票？") == "点击Yes":
            indexSelected = event.GetEventObject().GetSelections()
            event.GetEventObject().Delete(indexSelected[0])

    def _ev_group_analy(self, event):

        item = event.GetSelection()
        stock_set = self.listBox.GetStrings()

        ochl_paras = MarketGraphDialog(self, "行情走势参数配置")
        ochl_paras.Centre()
        # 第一步:收集控件中设置的选项
        if ochl_paras.ShowModal() != wx.ID_OK:
            return
        else:
            st_paras = ochl_paras.feedback_paras()

        # 第一步:收集控件中设置的选项
        st_period = st_paras["股票周期"]
        st_auth = st_paras["股票复权"]
        sdate_obj = st_paras["开始日期"]
        edate_obj = st_paras["结束日期"]

        if item == 1: # 显示收益率/波动率分布
            pct_chg = pd.DataFrame()

            for stock in stock_set:
                # 第二步:获取股票数据-调用sub event handle
                try:
                    pct_chg[stock] = self.call_method(self.event_task['get_stock_dat'],
                                                      st_code=stock.split("|")[0],
                                                      st_period=st_period,
                                                      st_auth=st_auth,
                                                      sdate_obj=sdate_obj,
                                                      edate_obj=edate_obj)['pctChg']
                except:
                    MessageDialog("[%s]涨幅数据获取失败！"%stock)

            # 计算股票收益率的均值和标准差
            rets = pct_chg.dropna()
            ret_mean = rets.mean()
            ret_std = rets.std()

            # 第三步:绘制可视化图形
            analy_group_pct = GroupPctDiag(self, u"多股收益率/波动率对比分析", stock_set, ret_mean, ret_std)
            """ 自定义提示框 """
            if analy_group_pct.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        elif item == 2:  # 显示走势叠加分析
            pct_chg = pd.DataFrame()
            for stock in stock_set:
                # 第二步:获取股票数据-调用sub event handle
                try:
                    pct_chg[stock] = (self.call_method(self.event_task['get_stock_dat'],
                                                      st_code=stock.split("|")[0],
                                                      st_period=st_period,
                                                      st_auth=st_auth,
                                                      sdate_obj=sdate_obj,
                                                      edate_obj=edate_obj)['pctChg']/ 100 + 1).cumprod()
                except:
                    MessageDialog("[%s]涨幅数据获取失败！"%stock)
            # 第三步:绘制可视化图形
            analy_group_pct = GroupTrendDiag(self, u"多股行情走势叠加对比分析", stock_set, pct_chg)
            """ 自定义提示框 """
            if analy_group_pct.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        elif item == 3:  # 显示财务指标评分
            pass

    def _ev_switch_menu(self, event):
        self.fun_swframe(0)  # 切换 Frame 主界面

    def _update_analyse_list(self, items):
        self.listBox.InsertItems(items, 0)  # 插入items

    def _add_analyse_list(self, item):

        if item in self.listBox.GetStrings():
            MessageDialog("股票%s已经存在！\n" % item)
        else:
            self.listBox.InsertItems([item], 0)  # 插入item

    def _ev_err_guide_menu(self, event):
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/113774922?spm=1001.2014.3001.5501')

    def _ev_funt_guide_menu(self, event):
        webbrowser.open('https://mp.weixin.qq.com/mp/homepage?__biz=MzUxMjU4NDAwNA==&hid=6&sn=81038d128b4ef94b01a1382e51359903')

    def _ev_import_code_menu(self, event):
        # 收集导入文件路径
        get_path = ImportFileDiag(pickout_path)

       # 加载csv文件中的数据
        if get_path != '':
            add_code = self.call_method(self.event_task['get_csvst_pool'], get_path=get_path)
            if add_code:
                # 完全替换/增量更新
                self._save_st_result("导入自选股票池模式", add_code)
            else:
                MessageDialog("文件内容为空！\n")

    def _ev_export_code_menu(self, event):

        if self.call_method(self.event_task['set_csvst_pool'], set_codes=self.self_pool.load_pool_stock()):
            self.syslog.re_print("我的自选股池导出成功，请在ConfigFlies目录下查看...")

    def _ev_click_menu_start(self, event):
        """
        菜单栏->开始下载->事件触发
        :param event:
        :return:
        """
        #choice_msg = ChoiceDialog("历史数据更新模式", [u"早期行情数据更新", u"仅当日行情数据更新"])
        choice_msg = u"早期行情数据更新"
        if choice_msg == u"早期行情数据更新":

            # 第一步: 收集控件中设置的选项
            update_dialog = SelectModeDialog(self, "更新数据参数配置")
            update_dialog.Centre()
            # 第一步:收集控件中设置的选项
            if update_dialog.ShowModal() != wx.ID_OK:
                return
            else:
                update_paras = update_dialog.feedback_paras()

            for code in self._select_pool_range(update_paras[u"股票池"], update_paras["过滤次新股上市时间"], update_paras["剔除ST股票"]):
                if q_paras.full() != True:
                    q_paras.put(code)

            self.progress = DownloadDataThread(self.update_download_ochlv_result, q_paras, "下载进度")
            self.progress.start()

            download_ochlv = HistoryOCHLV(data_path)
            for i in range(10):
                t = CrawlerThread(self, q_paras, q_results, download_ochlv.get_history_days_stock_data)
                t.start()

        elif choice_msg == u"仅当日行情数据更新":

            date_dialog = SelectModeDialog(self, "输入选股日期")

            date_dialog.Centre()
            # 第一步:收集控件中设置的选项
            if date_dialog.ShowModal() != wx.ID_OK:
                return
            else:
                sdate_obj = date_dialog.feedback_paras()
                sdate_val = datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)

                self.ts_data = self.crawer_backend["爬虫每日指标"](self.syslog)
                self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y-%m-%d'))  # 刷新self.df_join

                if self.df_join.empty == True:
                    MessageDialog("选股数据为空！请检查数据源是否有效！\n")
                    return
                else:

                    df_temp = self.df_join.assign(日期 = sdate_val.strftime('%Y-%m-%d')) # 新增一列

                    df_temp = df_temp.loc[:,['日期', '股票代码', '股票名称', '最新价格', '最高', '最低', '今开', '昨收', '涨跌额',
                                            '涨跌幅', '换手率', '成交量', '成交额', '总市值', '流通市值']]
                    df_temp.rename(columns={"股票名称": "名称", "最新价格": "收盘价", "最高": u"最高价", "最低": u"最低价",
                                            "今开": u"开盘价", "昨收": u"前收盘", "成交额": u"成交金额"},inplace=True)
                    # 数据获取正常后执行
                    for id, df_row in df_temp.iterrows():
                    #for code in self.code_table.stock_codes.values():
                        if q_paras.full() != True:
                            #q_paras.put(df_temp[df_temp["股票代码"] == code])
                            q_paras.put(df_row)

                    self.progress = DownloadDataThread(self.update_download_ochlv_result, q_paras, "下载进度")
                    self.progress.start()

                    download_ochlv = HistoryOCHLV(data_path)
                    for i in range(10):
                        t = CrawlerThread(self, q_paras, q_results, download_ochlv.update_latest_day_stock_data)
                        t.start()

        else:
            return

        self.syslog.re_print("离线行情数据下载正在执行...")
        self.start_time = time.perf_counter()

    def _ev_click_menu_fresh(self, event):
        """
        菜单栏->刷新文件->事件触发
        :param event:
        :return:
        """
        self.treeListStock.refDataShow(self.stock_tree_info)  # TreeCtrl显示数据接口

    def _ev_click_menu_compt(self, event):
        """
        菜单栏->补全下载->事件触发
        :param event:
        :return:
        """
        if self.failed_list != []:

            for code in self.failed_list:
                if q_paras.full() != True:
                    q_paras.put(code)

            self.progress = DownloadDataThread(self.update_download_ochlv_result, q_paras, "下载进度")
            self.progress.start()

            download_ochlv = HistoryOCHLV(data_path)
            t = CrawlerThread(self, q_paras, q_results, download_ochlv.get_history_days_stock_data)
            t.start()

            self.start_time = time.perf_counter()
        else:
            MessageDialog("补充下载列表为空! \n")

    def _ev_click_menu_stop(self, event):
        """
        菜单栏->停止下载->事件触发
        :param event:
        :return:
        """
        try:
            while not q_paras.empty():
                q_paras.get()
            self.syslog.re_print("离线行情数据下载紧急停止！")
        except Exception as e:
            print(e)

    def _patten_urgent_stop(self, cmd="init"):

        if cmd == "init":
            self.patten_drive_but.SetLabel(u"开始形态驱动选股")
            self.urgent_stop_flag = False
            return True
        else:
            if self.patten_drive_but.GetLabel() == u"开始形态驱动选股":
                self.patten_drive_but.SetLabel(u"停止形态驱动选股")
                self.urgent_stop_flag = False
                return False
            elif self.patten_drive_but.GetLabel() == u"停止形态驱动选股":
                self.patten_drive_but.SetLabel(u"开始形态驱动选股")
                self.urgent_stop_flag = True

                try:
                    while not q_paras.empty():
                        q_paras.get()
                    self.syslog.re_print("形态选股扫描紧急停止！")
                except Exception as e:
                    print(e)

                return True
            else:
                return True

    def _ev_adv_func(self, event):

        # 第一步:收集控件中设置的选项
        st_code = self.stock_code_cbox.GetValue()
        st_name = self.code_table.get_name(st_code)

        self.handle_active_code(st_code, st_name,  [u"添加自选股票池",
                                                    u"加入组合分析池",
                                                    u"查看现金流量",
                                                    u"查看行情走势",
                                                    u"查看F10资料",
                                                    u"K线自动播放",
                                                    u"导入离线数据"])

    def _ev_patten_save(self,event):
        pass

    def patten_analy_execute(self, stock_code):

        register_info = {"双底形态突破": Base_Patten_Group.double_bottom_search,
                         "箱体形态突破": Base_Patten_Group.bottom_average_break,
                         "单针探底回升": Base_Patten_Group.needle_bottom_raise,
                         "均线多头排列": Base_Patten_Group.mult_ma_raise,
                         "突破前期高点": Base_Patten_Group.new_high_break}

        try:
            st_period = self.patten_paras["股票周期"]
            st_auth = self.patten_paras["股票复权"]
            edate_obj = self.patten_paras["选股日期"]

            edate_val = datetime(edate_obj.year, edate_obj.month + 1, edate_obj.day)
            sdate_val = datetime(edate_obj.year-1, edate_obj.month + 1, edate_obj.day)

            st_name = self.code_table.get_name(stock_code)

            stock_dat = Csv_Backend.load_history_st_data(data_path + stock_code.replace(".", "") + '.csv',
                                                         sdate_val, edate_val, st_auth, st_period)

            df_return = register_info[self.patten_paras['选股模型']](st_name, stock_code, stock_dat, self.patlog,
                                                                  **self.patten_recognize)
        except Exception as e:
            print(stock_code, e)
            self.patlog.re_print(f"警告！{st_name} {stock_code}分析时数据有误！......\n")
            df_return = pd.DataFrame()

        return df_return # 有效则添加至分析结果文件中

    def patten_analy_result(self):

        self.elapsed_time = time.perf_counter()

        df_search = pd.DataFrame()  # 构建一个空的dataframe用来装数据

        while not q_results.empty():
            df_return = q_results.get()
            df_search = pd.concat([df_search, df_return], ignore_index=True, sort=False)

        if df_search.empty == True:
            MessageDialog("未筛选出符合条件股票！", "温馨提示")
            return

        select_date = datetime(self.patten_paras['选股日期'].year,
                               self.patten_paras['选股日期'].month + 1,
                               self.patten_paras['选股日期'].day)

        filter_columns = Base_File_Oper.load_sys_para("special_data_items.json")

        if self.patten_paras[u"北向资金持股"] == True:

            crawer_data = self.crawer_backend["爬虫北向资金"](self.syslog)
            df_north = crawer_data.datafame_join(select_date.strftime('%Y%m%d'))  # 刷新self.df_join
            if df_north.empty != True:
                df_north.drop('股票代码', axis=1, inplace=True)
                for key, val in filter_columns["今日北上资金"].items():
                    if val == "N": df_north.drop(key, axis=1, inplace=True)

                df_search = pd.merge(df_search, df_north, on=u'股票名称', left_index=False, right_index=False,
                                    how='left')

        if self.patten_paras[u"每日基本面指标"] == True:
            crawer_data = self.crawer_backend["爬虫每日指标"](self.syslog)
            df_basic = crawer_data.datafame_join(select_date.strftime('%Y%m%d'))  # 刷新self.df_join
            if df_basic.empty != True:
                df_basic.drop('股票代码', axis=1, inplace=True)

                for key, val in filter_columns["每日基本面指标"].items():
                    if val == "N": df_basic.drop(key, axis=1, inplace=True)

                df_search = pd.merge(df_search, df_basic, on=u'股票名称', left_index=False, right_index=False,
                                    how='inner')

        if self.patten_paras[u"叠加利润报表"] == True:

            store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/FinanceData/'
            operate_sqlite = DataBase_Sqlite(store_path + u'finance_data_quarter.db')
            df_profit = operate_sqlite.read_table("newest_quarter_profit_report")
            if df_profit.empty != True:
                df_profit.drop('股票代码', axis=1, inplace=True)

                for key, val in filter_columns["季度利润报表"].items():
                    if val == "N": df_profit.drop(key, axis=1, inplace=True)
                df_search = pd.merge(df_search, df_profit, on=u'股票名称', left_index=False, right_index=False,
                                    how='left')


        """
        if patten_recognize.feedback_paras()[u"叠加基金持仓"] == True:
            store_path = os.path.dirname(os.path.dirname(__file__)) + '/DataFiles/FinanceData/'
            operate_sqlite = DataBase_Sqlite(store_path + u'finance_data_quarter.db')
            df_profit = operate_sqlite.read_table("newest_quarter_profit_report")
            df_profit.drop('股票代码', axis=1, inplace=True)

            df_search = pd.merge(df_search, df_profit, on=u'股票名称', left_index=False, right_index=False,
                                how='inner')
        """

        Base_File_Oper.save_patten_analysis(df_search, f"{self.patten_paras['选股模型']}分析结果_{select_date.strftime('%Y-%m-%d')}_高速版")
        self.patlog.re_print("\n形态分析完成！明细查看路径ConfigFiles/全市场选股结果/")

        self.tran_col = dict(zip(df_search.columns.tolist(), df_search.columns.tolist()))
        self.filter = df_search.columns.tolist()
        self.df_use = df_search
        self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

        # sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        # auto_send_email('主人！你的双底形态分析报告来啦', "\n形态分析明细查看ConfigFiles/全市场选股结果/双底形态分析结果-高速版.csv",
        #                 f"{select_date.strftime('%Y-%m-%d')}_{self.patten_paras['选股模型']}分析结果_高速版.csv",
        #                 self.patlog, **sys_para["mailbox"])

        self._patten_urgent_stop("init")

    def backtest_stock_execute(self, paras_list):

        try:
            stock_code, output_date = paras_list[0], paras_list[1]

            st_name = self.code_table.get_name(stock_code)

            sdate_val = datetime.strptime(output_date, "%Y-%m-%d")
            stock_dat = Csv_Backend.load_history_st_data(data_path + stock_code.replace(".", "") + '.csv',
                                                         sdate_val, "", "前复权", "日线")

            back_min_close_val = round(stock_dat['收盘价'].min(),2),
            back_max_close_val = round(stock_dat['收盘价'].max(),2),
            select_close_val = round(stock_dat["收盘价"][0], 2),
            newest_close_val = round(stock_dat["收盘价"][-1], 2),

            select_close_id = output_date
            newest_close_id = stock_dat.index[-1].strftime("%Y-%m-%d"),
            back_min_close_id = stock_dat['收盘价'].idxmin().strftime("%Y-%m-%d")
            back_max_close_id = stock_dat['收盘价'].idxmax().strftime("%Y-%m-%d")

            max_profit = round(((back_max_close_val[0] - select_close_val[0]) / select_close_val[0] * 100) if back_max_close_val[0] > select_close_val[0] else 0,
                               2)
            max_retrace = round(((back_min_close_val[0] - select_close_val[0]) / select_close_val[0] * 100) if select_close_val[0] > back_min_close_val[0] else 0,
                             2)
            # 最新盈亏
            latest_profit = round(((newest_close_val[0] - select_close_val[0])/select_close_val[0] * 100), 2)

            monitor_info = []
            monitor_info.append([st_name,
                                 select_close_id,
                                 select_close_val[0],
                                 newest_close_id[0],
                                 newest_close_val[0],
                                 back_max_close_val[0], back_max_close_id,
                                 back_min_close_val[0], back_min_close_id,
                                 max_profit, max_retrace, latest_profit])

            df_return = pd.DataFrame(monitor_info, index=[stock_code],
                              columns=['股票名称', '出票时间', '出票价格', '当前时间', '当前价格',
                                       '最高价格', '最高时间', '最低价格', '最低时间',
                                       '最大收益%', '最大回撤%', '当前收益%'])

        except Exception as e:
            print(e)
            self.patlog.re_print(f"警告！{st_name} {stock_code}分析时数据有误！......\n")
            df_return = pd.DataFrame()

        return df_return  # 有效则添加至分析结果文件中

    def backtest_stock_result(self):

        self.elapsed_time = time.perf_counter()

        df_search = pd.DataFrame()  # 构建一个空的dataframe用来装数据

        while not q_results.empty():
            df_return = q_results.get()
            df_search = pd.concat([df_search, df_return], ignore_index=False, sort=False)

        if df_search.empty == True:
            MessageDialog("未找到需要计算收益的股票！", "温馨提示")
            return

        view_stock_data = ViewListDiag(self, u"监测股票收益", df_search)
        view_stock_data.Centre()
        """ 自定义提示框 """
        if view_stock_data.ShowModal() == wx.ID_OK:
            pass

    def _select_pool_range(self, pool_type, date_lim, st_rm)->list:

        # 获取当前所有非新股/次新股代码和名称 剔除ST股票
        code_name = self.code_table.specific_stock_code(date_lim, st_rm)

        if pool_type == "自选股票池":
            dict_pool = self.self_pool.load_pool_stock()
            dict_basic = dict(zip(code_name.values(), code_name.keys())).keys() & \
                         dict(zip(dict_pool.values(), dict_pool.keys())).keys()
            code_list = list(dict_basic)

        elif pool_type == "全市场股票":
            code_list = list(code_name.values())

        elif (pool_type == "概念板块池") or (pool_type == "行业板块池"):

            json_path = {"概念板块池":"concept_code_map.json", "行业板块池":"industry_code_map.json"}
            map_table = Base_File_Oper.load_sys_para(json_path[pool_type])

            classify_select = ClassifySelectDiag(self, pool_type, map_table)
            classify_select.ShowModal()

            map_table = classify_select.feedback_map()
            Base_File_Oper.save_sys_para(json_path[pool_type], map_table)

            set_basic = set()
            for val in map_table["已选择"].values():
                set_basic.update(list(val.values()))

            dict_basic = dict(zip(code_name.values(), code_name.keys())).keys() & set_basic
            code_list = list(dict_basic)
        else:
            code_list = []

        return code_list


    def _ev_patten_select_func(self, event):

        if self._patten_urgent_stop("detect") == True:
            return

        # 第一步: 收集控件中设置的选项
        patten_dialog = SelectModeDialog(self, "形态选股参数配置")
        patten_dialog.Centre()
        # 第一步:收集控件中设置的选项
        if patten_dialog.ShowModal() != wx.ID_OK:
            self._patten_urgent_stop("init")
            return
        else:
            pat_paras = patten_dialog.feedback_paras()

        # 第一步:收集控件中设置的选项
        patten_pool = pat_paras["股票池"]
        patten_type = pat_paras["选股模型"]

        #MessageDialog("为解决全市场股票扫描时的效率问题，日线周期默认使用本地股票数据！", "温馨提示")
        dict_basic = self._select_pool_range(patten_pool, pat_paras["过滤次新股上市时间"], pat_paras["剔除ST股票"])

        self.patlog.clr_print()
        self.patlog.re_print(f"启动{patten_pool} 选股模型分析......\n")

        self.LogNoteb.SetSelection(1)

        register_info = {"双底形态突破": {"对话框函数": DouBottomDialog,
                                        "日志信息":"双底形态选股正在执行..."},
                         "箱体形态突破":{"对话框函数": BreakBottomDialog,
                                        "日志信息":"底部形态选股正在执行..."},
                         "均线多头排列": {"对话框函数": MultMaRiseDialog,
                                        "日志信息": "均线多头排列选股正在执行..."},
                         "单针探底回升": {"对话框函数": NeedleBottomDialog,
                                    "日志信息": "单针探底回升选股正在执行..."},
                         "突破前期高点": {"对话框函数": NewHighBreakDialog,
                                    "日志信息": "突破前期高点选股正在执行..."},
                         }

        patten_recognize = register_info[patten_type]["对话框函数"](self, f"{patten_type}识别参数配置")
        patten_recognize.Centre()
        if patten_recognize.ShowModal() == wx.ID_OK:
            self.patten_recognize = patten_recognize.feedback_paras()
            self.patten_paras = pat_paras
        else:
            return

        for stock_code in dict_basic:
            if q_paras.full() != True:
                q_paras.put(self.code_table.conv_ts_code(stock_code))

        self.progress = DownloadDataThread(self.patten_analy_result, q_paras, "选股进度")
        self.progress.start()

        for i in range(3):
            t = CrawlerThread(self, q_paras, q_results, self.patten_analy_execute)
            t.start()

        self.patlog.re_print(register_info[patten_type]["日志信息"])
        self.start_time = time.perf_counter()

    def _ev_rps_select_func(self, event):

        # 第一步: 收集控件中设置的选项
        patten_paras = SelectModeDialog(self, "RPS选股参数配置")
        patten_paras.Centre()
        # 第一步:收集控件中设置的选项
        if patten_paras.ShowModal() != wx.ID_OK:
            return
        else:
            pat_paras = patten_paras.feedback_paras()

        # 第一步:收集控件中设置的选项
        self.patlog.clr_print()
        self.patlog.re_print(f"启动{pat_paras['选股模型']} 选股模型分析......\n")

        self.LogNoteb.SetSelection(1)

        if pat_paras["选股模型"] == "个股历史RPS排名":

            rpstop_recognize = RpsTopNDialog(self, "个股历史RPS排名参数配置")
            rpstop_recognize.Centre()

            if rpstop_recognize.ShowModal() == wx.ID_OK:

                rps_para = rpstop_recognize.feedback_paras()

                df_search = Base_File_Oper.load_patten_analysis(f"计算RPS使用的涨跌幅数据")  # 构建一个dataframe用来装涨跌幅数据
                df_search = df_search.reindex(columns=df_search.columns)
                df_search.dropna(how='all', axis=1, inplace=True)

                # if pat_paras[u"剔除ST股票"] == True:
                #     # 剔除ST股票(前面已经剔除, 此处删除也可以)
                #     df_search = df_search.loc[:, list(map(lambda x: x.find('ST') < 0, df_search.columns))]

                df_search = df_search.fillna(0)
                df_compete = df_search.copy(deep=True)
                df_search = df_search.rolling(window=pat_paras["选取涨跌幅滚动周期"]).mean().round(2)

                start_date = datetime(pat_paras['开始日期'].year,
                                       pat_paras['开始日期'].month + 1,
                                       pat_paras['开始日期'].day)

                select_date = datetime(pat_paras['选股日期'].year,
                                       pat_paras['选股日期'].month + 1,
                                       pat_paras['选股日期'].day)

                if len(df_search) > pat_paras["选取涨跌幅滚动周期"]:
                    df_search = df_search[-(len(df_search) - pat_paras["选取涨跌幅滚动周期"]):].fillna(0)
                else:
                    MessageDialog(f"选取涨跌幅滚动周期({pat_paras['选取涨跌幅滚动周期']}) 大于行情数据量！", "温馨提示")
                    return

                if (select_date - start_date).days > 0:
                    df_search = df_search.loc[start_date:select_date, :]
                    df_compete = df_compete.loc[start_date:select_date, :]

                df_return = Base_Indicate_Group.rps_top10_order(df_search, rps_para["选取显示的排名范围"])

                if df_return.empty != True:

                    self.tran_col = dict(zip(df_return.columns.tolist(), df_return.columns.tolist()))
                    self.df_use = df_return
                    self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

                    self.patlog.re_print(
                        f"\n个股历史RPS排名分析完成！排名明细查看ConfigFiles/全市场选股结果/个股历史RPS—Top{rps_para['选取显示的排名范围']}分析结果-高速版.csv")
                    Base_File_Oper.save_patten_analysis(df_return, f"个股历史RPS_Top_{rps_para['选取显示的排名范围']}分析结果{select_date.strftime('%Y-%m-%d')}_高速版")

                    if MessageDialog('是否查看动画版RPS指标-龙头股竞赛', u"温馨提示") == "点击Yes":
                        dialog = RpsCompeteDialog(self, u"RPS动画-龙头股竞赛", df_compete)
                        dialog.Show()
                else:
                    self.patlog.re_print(f"\n个股历史RPS排名结果为空！")

        else:
            return

    def _ev_backtest_select_func(self, event):

        MessageDialog("注意：当前仅支持形态选股(箱体形态/双底形态/均线发散)结果的回测！")

        # 第一步:收集导入文件路径
        get_path = ImportFileDiag(pickout_path)

        if get_path != '':

            m = re.match(r'.*_(\d{4})-(\d{2})-(\d{2})_', get_path)
            if m is not None:
                output_date = f"{m.groups()[0]}-{m.groups()[1]}-{m.groups()[2]}"
            else:
                return

            self.ts_data = Csv_Backend("回测选股结果")
            self.df_join = self.ts_data.load_pick_data(get_path)

            for stock_code in self.df_join["股票代码"]:
                if q_paras.full() != True:
                    q_paras.put([self.code_table.conv_ts_code(stock_code), output_date])

            self.progress = DownloadDataThread(self.backtest_stock_result, q_paras, "回测进度")
            self.progress.start()

            for i in range(1):
                t = CrawlerThread(self, q_paras, q_results, self.backtest_stock_execute)
                t.start()

            self.patlog.re_print("启动选股模型回测评估......")
            self.start_time = time.perf_counter()