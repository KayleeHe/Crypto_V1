#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from CommIf.SysFile import Base_File_Oper
from MainlyGui.ElementGui.DefPanel import GroupPanel, MergePanel
# 分离控件事件中调用的子事件
from EventEngine.DefEvent import EventHandle
from MultiGraphs.SignalOutput import CurHaveSig

class GroupPctDiag(wx.Dialog):  # 多股收益率/波动率分析

    def __init__(self, parent, title=u"自定义提示信息", set_stocks=[], mean_val=[], std_val=[], size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.stock_set = set_stocks
        self.mean = mean_val
        self.std = std_val

        self.GroupPanel = GroupPanel(self)  # 自定义
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.GroupPanel, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.draw_figure()

    def draw_figure(self):

        self.GroupPanel.relate.clear()
        self.GroupPanel.relate.scatter(self.mean, self.std, marker='o',
                                       c=np.linspace(0.1, 1, len(self.stock_set)),
                                       s=500,
                                       cmap=plt.get_cmap('Spectral'))

        self.GroupPanel.relate.set_xlabel("均值%")
        self.GroupPanel.relate.set_ylabel("标准差%")

        for label, x, y in zip(self.stock_set, self.mean, self.std):
            self.GroupPanel.relate.annotate(label, xy=(x, y), xytext=(20, 20),
                                            textcoords="offset points",
                                            ha="right", va="bottom",
                                            bbox=dict(boxstyle='round, pad=0.5',
                                                      fc='red', alpha=0.2),
                                            arrowprops=dict(arrowstyle="->",
                                                            connectionstyle="arc3,rad=0.3"))
        self.GroupPanel.FigureCanvas.draw()

class GroupTrendDiag(wx.Dialog):  # 行情走势叠加分析

    def __init__(self, parent, title=u"自定义提示信息", set_stocks=[], df_stcok=[], size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.stock_set = set_stocks
        self.df_stcok = df_stcok

        self.GroupPanel = GroupPanel(self)  # 自定义
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.GroupPanel, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.draw_figure()

    def draw_figure(self):

        self.GroupPanel.relate.clear()
        self.df_stcok.plot(ax=self.GroupPanel.relate)

        self.GroupPanel.relate.set_xlabel("日期")
        self.GroupPanel.relate.set_ylabel("归一化走势")

        self.GroupPanel.FigureCanvas.draw()

class UserDialog(wx.Dialog):  # user-defined

    def __init__(self, parent, title=u"自定义提示信息", label=u"自定义日志", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.log_tx_input = wx.TextCtrl(self, -1, "", size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)  # 多行|只读
        self.log_tx_input.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()

        self.dialog_info_box = wx.StaticBox(self, -1, label)
        self.dialog_info_sizer = wx.StaticBoxSizer(self.dialog_info_box, wx.VERTICAL)
        self.dialog_info_sizer.Add(self.log_tx_input, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        self.dialog_info_sizer.Add(self.ok_btn, proportion=0, flag=wx.ALIGN_CENTER)
        self.SetSizer(self.dialog_info_sizer)

        self.disp_loginfo()

    def disp_loginfo(self):
        self.log_tx_input.Clear()
        self.log_tx_input.AppendText(Base_File_Oper.read_log_trade())

class ScanDialog(wx.Dialog):  # user-defined

    def __init__(self, parent, st_label, st_codes, st_period, st_auth, sdate_obj, edate_obj, title=u"自定义提示信息", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 初始化事件调用接口
        self.EventHandle = EventHandle()
        self.call_method = self.EventHandle.call_method
        self.event_task = self.EventHandle.event_task

        self.cur_have_sig = CurHaveSig()

        self.trade_paras_sizer = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)

        # 设置买入条件参数
        self.buy_slippage_box = wx.StaticBox(self, -1, u'设置买入滑点(%)')
        self.buy_slippage_sizer = wx.StaticBoxSizer(self.buy_slippage_box, wx.VERTICAL)
        self.buy_slippage_input = wx.TextCtrl(self, -1, "2", style=wx.TE_PROCESS_ENTER)
        self.buy_slippage_sizer.Add(self.buy_slippage_input, proportion=0, flag=wx.ALIGN_CENTER)

        self.buy_amount_box = wx.StaticBox(self, -1, u'设置买入股数(手)')
        self.buy_amount_sizer = wx.StaticBoxSizer(self.buy_amount_box, wx.VERTICAL)
        self.buy_amount_input = wx.TextCtrl(self, -1, "100", style=wx.TE_PROCESS_ENTER)
        self.buy_amount_sizer.Add(self.buy_amount_input, proportion=0, flag=wx.ALIGN_CENTER)

        # 设置卖出条件参数
        self.sell_slippage_box = wx.StaticBox(self, -1, u'设置卖出滑点(%)')
        self.sell_slippage_sizer = wx.StaticBoxSizer(self.sell_slippage_box, wx.VERTICAL)
        self.sell_slippage_input = wx.TextCtrl(self, -1, "2", style=wx.TE_PROCESS_ENTER)
        self.sell_slippage_sizer.Add(self.sell_slippage_input, proportion=0, flag=wx.ALIGN_CENTER)

        self.sell_amount_box = wx.StaticBox(self, -1, u'设置卖出股数(手)')
        self.sell_amount_sizer = wx.StaticBoxSizer(self.sell_amount_box, wx.VERTICAL)
        self.sell_amount_input = wx.TextCtrl(self, -1, "100", style=wx.TE_PROCESS_ENTER)
        self.sell_amount_sizer.Add(self.sell_amount_input, proportion=0, flag=wx.ALIGN_CENTER)

        self.start_btn = wx.Button(self, -1, u"开始扫描")
        self.start_btn.SetDefault()
        self.start_btn.Bind(wx.EVT_BUTTON, self.ev_start)
        self.ok_btn = wx.Button(self, wx.ID_OK, u"取消")

        self.trade_paras_sizer.Add(self.buy_slippage_sizer, proportion=0, flag=wx.ALIGN_CENTER)
        self.trade_paras_sizer.Add(self.buy_amount_sizer, proportion=0, flag=wx.ALIGN_CENTER)
        self.trade_paras_sizer.Add(self.sell_slippage_sizer, proportion=0, flag=wx.ALIGN_CENTER)
        self.trade_paras_sizer.Add(self.sell_amount_sizer, proportion=0, flag=wx.ALIGN_CENTER)

        self.trade_paras_sizer.Add(self.start_btn, proportion=0, flag=wx.ALIGN_CENTER)
        self.trade_paras_sizer.Add(self.ok_btn, proportion=0, flag=wx.ALIGN_CENTER)

        self.log_tx_input = wx.TextCtrl(self, -1, "", size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)  # 多行|只读
        self.log_tx_input.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.dialog_info_box = wx.StaticBox(self, -1, "信号生成明细")
        self.dialog_info_sizer = wx.StaticBoxSizer(self.dialog_info_box, wx.VERTICAL)
        self.dialog_info_sizer.Add(self.trade_paras_sizer, proportion=0, flag=wx.EXPAND|wx.ALL|wx.CENTER, border=10)
        self.dialog_info_sizer.Add(self.log_tx_input, proportion=0, flag=wx.ALIGN_CENTER)

        self.SetSizerAndFit(self.dialog_info_sizer)

        # 初始化变量
        self.st_codes = st_codes
        self.st_period = st_period
        self.st_auth = st_auth
        self.sdate_obj = sdate_obj
        self.edate_obj = edate_obj
        self.st_label = st_label
        self.trade_para = {}

    @property
    def generate_codes(self):
        for code in self.st_codes.values():
            yield code

    def ev_start(self, event):

        if self.start_btn.GetLabel() == u"开始扫描":
            self.start_btn.SetLabel(u"停止扫描")

            # 开启定时器
            self.analy_timer = wx.Timer(self)  # 创建定时器
            self.Bind(wx.EVT_TIMER, self.ev_analy_timer, self.analy_timer)  # 绑定一个定时器事件
            self.gen_code = self.generate_codes
            self.analy_timer.Start(200)  # 启动定时器

        elif self.start_btn.GetLabel() == u"停止扫描":
            self.start_btn.SetLabel(u"开始扫描")
            self.analy_timer.Stop()  # 关闭定时器
            self.log_tx_input.AppendText("取消运行！\n")
            #self.Destroy()

    def ev_analy_timer(self, event):

        try:
            code = next(self.gen_code)

            # 第二步:获取股票数据-调用sub event handle
            stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                              st_code=code,
                                              st_period=self.st_period,
                                              st_auth=self.st_auth,
                                              sdate_obj=self.sdate_obj,
                                              edate_obj=self.edate_obj)

            view_function = self.cur_have_sig.ind.route_output(self.st_label)
            cont = view_function(stock_dat)
            self.log_tx_input.AppendText(code + " " + cont)

            if "买入" in cont:
                self.trade_para[code] = {}
                self.trade_para[code][u"code"] = code
                self.trade_para[code][u"direct"] = "买"
                self.trade_para[code][u"close"] = np.round(stock_dat["Close"][-1], 2)
                self.trade_para[code][u"price"] = np.round(stock_dat["Close"][-1]*(1+float(self.buy_slippage_input.GetValue())/100), 2)
                self.trade_para[code][u"amount"] = int(self.buy_amount_input.GetValue())
                self.trade_para[code][u"trace_strategy"] = "自定义策略1"
                self.trade_para[code][u"auto_trade"] = "否"

                self.log_tx_input.AppendText(code + " 添加至监测股票池, 准备在实盘时买入！\n")

            elif "卖出" in cont:
                self.trade_para[code] = {}
                self.trade_para[code][u"code"] = code
                self.trade_para[code][u"direct"] = "卖"
                self.trade_para[code][u"close"] = np.round(stock_dat["Close"][-1], 2)
                self.trade_para[code][u"price"] = np.round(stock_dat["Close"][-1]*(1-float(self.sell_slippage_input.GetValue())/100), 2)
                self.trade_para[code][u"amount"] = int(self.sell_amount_input.GetValue())
                self.trade_para[code][u"trace_strategy"] = "自定义策略1"
                self.trade_para[code][u"auto_trade"] = "否"

                self.log_tx_input.AppendText(code + " 添加至监测股票池, 准备在实盘时卖出！\n")

        except Exception as e:
            self.analy_timer.Stop()  # 关闭定时器
            self.log_tx_input.AppendText("自选股票池扫描完成！\n")
            print(e)

    def back_results(self):
        return self.trade_para

class BrowserF10(wx.Dialog):

    def __init__(self, parent, title=u"自定义提示信息", code="300180", size=(1000, 800)):
        super(BrowserF10, self).__init__(None, title=title, size=size)

        if '.' in code:
            code = code.split('.')[0]

            if (code[0] == "3" or code[0] == "0" or code[0] == "6") and (len(code) == 6):
                self.code = code

                sizer = wx.BoxSizer(wx.VERTICAL)
                self.browser = wx.html2.WebView.New(self, -1, size=size)
                sizer.Add(self.browser, 1, wx.EXPAND, 10)
                self.SetSizer(sizer)
                self.SetSize((1000, 800))
                self.load_f10()

    def load_f10(self):

        self.browser.LoadURL("http://basic.10jqka.com.cn/" + self.code + "/operate.html#intro")  # 加载页面

class WebDialog(wx.Dialog):  # user-defined

    load_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))\
                + '/DataFiles/'

    def __init__(self, parent, title=u"Web显示", file_name='treemap_base.html', size=(1200, 900)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.browser = wx.html2.WebView.New(self, -1, size=size)
        with open(self.load_path + file_name, 'r') as f:
            html_cont = f.read()
        self.browser.SetPage(html_cont, "")
        self.browser.Show()

class DouBottomDialog(wx.Dialog):  # 双底形态参数

    load_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) \
                + '/ConfigFiles/'

    def __init__(self, parent, title=u"自定义提示信息", size=(900, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style = wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=0, hgap=0)

        # 选取K线范围
        self.period_amount_box = wx.StaticBox(self, -1, "选取K线范围(日)")
        self.period_amount_sizer = wx.StaticBoxSizer(self.period_amount_box, wx.VERTICAL)
        self.period_amount_input = wx.TextCtrl(self, -1, "40", style=wx.TE_PROCESS_ENTER)
        self.period_amount_sizer.Add(self.period_amount_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 选取中间区域误差
        self.middle_err_box = wx.StaticBox(self, -1, "选取中间区域误差(日)")
        self.middle_err_sizer = wx.StaticBoxSizer(self.middle_err_box, wx.VERTICAL)
        self.middle_err_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.middle_err_sizer.Add(self.middle_err_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 双底低点之间误差
        self.lowbetw_err_box = wx.StaticBox(self, -1, "双底低点之间误差%")
        self.lowbetw_err_sizer = wx.StaticBoxSizer(self.lowbetw_err_box, wx.VERTICAL)
        self.lowbetw_err_input = wx.TextCtrl(self, -1, "2", style=wx.TE_PROCESS_ENTER)
        self.lowbetw_err_sizer.Add(self.lowbetw_err_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 有效突破颈线幅度
        self.backcfm_thr_box = wx.StaticBox(self, -1, "有效突破颈线幅度%")
        self.backcfm_thr_sizer = wx.StaticBoxSizer(self.backcfm_thr_box, wx.VERTICAL)
        self.backcfm_thr_input = wx.TextCtrl(self, -1, "3", style=wx.TE_PROCESS_ENTER)
        self.backcfm_thr_sizer.Add(self.backcfm_thr_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 有效突破当天涨跌幅
        self.break_pctchg_box = wx.StaticBox(self, -1, "有效突破当天涨跌幅%")
        self.break_pctchg_sizer = wx.StaticBoxSizer(self.break_pctchg_box, wx.VERTICAL)
        self.break_pctchg_input = wx.TextCtrl(self, -1, "1", style=wx.TE_PROCESS_ENTER)
        self.break_pctchg_sizer.Add(self.break_pctchg_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 有效突破成交量阈值
        self.volume_thr_box = wx.StaticBox(self, -1, "有效突破成交量阈值(大于平均%)")
        self.volume_thr_sizer = wx.StaticBoxSizer(self.volume_thr_box, wx.VERTICAL)
        self.volume_thr_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.volume_thr_sizer.Add(self.volume_thr_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 设置使能回测所需交易日
        # self.backtest_days_box = wx.StaticBox(self, -1, "设置使能回测所需交易日数量")
        # self.backtest_days_sizer = wx.StaticBoxSizer(self.backtest_days_box, wx.VERTICAL)
        # self.backtest_days_input = wx.TextCtrl(self, -1, "40", style=wx.TE_PROCESS_ENTER)
        # self.backtest_days_sizer.Add(self.backtest_days_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        self.save_cond_box = wx.RadioBox(self, -1, label=u'选股结果保存', choices=["满足突破幅度就保存", "满足首次突破才保存"],
                                                                     majorDimension = 2, style = wx.RA_SPECIFY_ROWS)

        self.vbox_sizer_but = wx.BoxSizer(wx.VERTICAL) # 纵向box
        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")
        self.vbox_sizer_but.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL|wx.EXPAND)
        self.vbox_sizer_but.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL|wx.EXPAND)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.period_amount_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.middle_err_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.lowbetw_err_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.backcfm_thr_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.break_pctchg_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.volume_thr_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        #self.FlexGridSizer.Add(self.backtest_days_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.save_cond_box, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.vbox_sizer_but, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        # 声明图片对象
        image = wx.Image(self.load_path+r'双底形态识别模型图.png', wx.BITMAP_TYPE_PNG)
        #print('图片的尺寸为{0}x{1}'.format(image.GetWidth(),image.GetHeight()))

        image.Rescale(image.GetWidth(),image.GetHeight())
        embed_pic = image.ConvertToBitmap()
        # 显示图片
        self.embed_bitmap = wx.StaticBitmap(self, -1, bitmap=embed_pic, size=(image.GetWidth(), image.GetHeight()))

        # 添加参数布局
        self.vbox_sizer = wx.BoxSizer(wx.HORIZONTAL)  # 纵向box
        self.vbox_sizer.Add(self.FlexGridSizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=1)
        self.vbox_sizer.Add(self.embed_bitmap, proportion=1, flag=wx.EXPAND | wx.ALL, border=1)
        self.SetSizer(self.vbox_sizer)

    def feedback_paras(self):

        self.bottom_para = dict()

        self.bottom_para[u"选取K线范围"] = int(self.period_amount_input.GetValue())
        self.bottom_para[u"选取中间区域误差"] = int(self.middle_err_input.GetValue())
        self.bottom_para[u"双底低点之间误差"] = float(self.lowbetw_err_input.GetValue())
        self.bottom_para[u"有效突破当天涨跌幅"] = float(self.break_pctchg_input.GetValue())
        self.bottom_para[u"有效突破颈线幅度"] = int(self.backcfm_thr_input.GetValue())
        self.bottom_para[u"有效突破成交量阈值"] = float(self.volume_thr_input.GetValue())
        #self.bottom_para[u"双底回测使能所需交易日"] = int(self.backtest_days_input.GetValue())
        self.bottom_para[u"选股结果保存"] = self.save_cond_box.GetStringSelection()

        return self.bottom_para

class BreakBottomDialog(wx.Dialog):  # 底部平台突破参数

    def __init__(self, parent, title=u"自定义提示信息", size=(500, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=5, cols=2, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 突破区间窗口
        self.break_range_box = wx.StaticBox(self, -1, "选取突破区间窗口")
        self.break_range_sizer = wx.StaticBoxSizer(self.break_range_box, wx.VERTICAL)
        self.break_range_input = wx.TextCtrl(self, -1, "40", style=wx.TE_PROCESS_ENTER)
        self.break_range_sizer.Add(self.break_range_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第一条均线周期
        self.first_average_box = wx.StaticBox(self, -1, "选取第一条均线周期")
        self.first_average_sizer = wx.StaticBoxSizer(self.first_average_box, wx.VERTICAL)
        self.first_average_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.first_average_sizer.Add(self.first_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第二条均线周期
        self.second_average_box = wx.StaticBox(self, -1, "选取第二条均线周期")
        self.second_average_sizer = wx.StaticBoxSizer(self.second_average_box, wx.VERTICAL)
        self.second_average_input = wx.TextCtrl(self, -1, "30", style=wx.TE_PROCESS_ENTER)
        self.second_average_sizer.Add(self.second_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第三条均线周期
        self.third_average_box = wx.StaticBox(self, -1, "选取第三条均线周期")
        self.third_average_sizer = wx.StaticBoxSizer(self.third_average_box, wx.VERTICAL)
        self.third_average_input = wx.TextCtrl(self, -1, "60", style=wx.TE_PROCESS_ENTER)
        self.third_average_sizer.Add(self.third_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第四条均线周期
        self.fourth_average_box = wx.StaticBox(self, -1, "选取第四条均线周期")
        self.fourth_average_sizer = wx.StaticBoxSizer(self.fourth_average_box, wx.VERTICAL)
        self.fourth_average_input = wx.TextCtrl(self, -1, "120", style=wx.TE_PROCESS_ENTER)
        self.fourth_average_sizer.Add(self.fourth_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 上下波动幅度
        self.wave_range_box = wx.StaticBox(self, -1, "选取底部箱体上下波动幅度(小于%)")
        self.wave_range_sizer = wx.StaticBoxSizer(self.wave_range_box, wx.VERTICAL)
        self.wave_range_input = wx.TextCtrl(self, -1, "15", style=wx.TE_PROCESS_ENTER)
        self.wave_range_sizer.Add(self.wave_range_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 均线粘合幅度
        self.average_bond_box = wx.StaticBox(self, -1, "选取均线粘合幅度(小于%)")
        self.average_bond_sizer = wx.StaticBoxSizer(self.average_bond_box, wx.VERTICAL)
        self.average_bond_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.average_bond_sizer.Add(self.average_bond_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 突破时涨幅
        self.break_pctchg_box = wx.StaticBox(self, -1, "选取平台突破时涨幅(大于%)")
        self.break_pctchg_sizer = wx.StaticBoxSizer(self.break_pctchg_box, wx.VERTICAL)
        self.break_pctchg_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.break_pctchg_sizer.Add(self.break_pctchg_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.break_range_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.first_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.second_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.third_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.fourth_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.wave_range_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.average_bond_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.break_pctchg_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        self.break_para = dict()

        self.break_para[u"突破区间窗口"] = int(self.break_range_input.GetValue())
        self.break_para[u"第一条均线周期"] = int(self.first_average_input.GetValue())
        self.break_para[u"第二条均线周期"] = int(self.second_average_input.GetValue())
        self.break_para[u"第三条均线周期"] = int(self.third_average_input.GetValue())
        self.break_para[u"第四条均线周期"] = int(self.fourth_average_input.GetValue())
        self.break_para[u"上下波动幅度"] = int(self.wave_range_input.GetValue())
        self.break_para[u"均线粘合幅度"] = int(self.average_bond_input.GetValue())
        self.break_para[u"突破时涨幅"] = int(self.break_pctchg_input.GetValue())

        return self.break_para

class MultMaRiseDialog(wx.Dialog):  # 多均线发散参数

    def __init__(self, parent, title=u"自定义提示信息", size=(500, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=8, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 第一条均线周期
        self.first_average_box = wx.StaticBox(self, -1, "选取第一条均线周期")
        self.first_average_sizer = wx.StaticBoxSizer(self.first_average_box, wx.VERTICAL)
        self.first_average_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.first_average_sizer.Add(self.first_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第二条均线周期
        self.second_average_box = wx.StaticBox(self, -1, "选取第二条均线周期")
        self.second_average_sizer = wx.StaticBoxSizer(self.second_average_box, wx.VERTICAL)
        self.second_average_input = wx.TextCtrl(self, -1, "10", style=wx.TE_PROCESS_ENTER)
        self.second_average_sizer.Add(self.second_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第三条均线周期
        self.third_average_box = wx.StaticBox(self, -1, "选取第三条均线周期")
        self.third_average_sizer = wx.StaticBoxSizer(self.third_average_box, wx.VERTICAL)
        self.third_average_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.third_average_sizer.Add(self.third_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 第四条均线周期
        self.fourth_average_box = wx.StaticBox(self, -1, "选取第四条均线周期")
        self.fourth_average_sizer = wx.StaticBoxSizer(self.fourth_average_box, wx.VERTICAL)
        self.fourth_average_input = wx.TextCtrl(self, -1, "30", style=wx.TE_PROCESS_ENTER)
        self.fourth_average_sizer.Add(self.fourth_average_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 持续检测天数
        self.continue_days_box = wx.StaticBox(self, -1, "持续发散的天数")
        self.continue_days_sizer = wx.StaticBoxSizer(self.continue_days_box, wx.VERTICAL)
        self.continue_days_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.continue_days_sizer.Add(self.continue_days_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 发散开口幅度(倍)
        self.enlarge_scope_box = wx.StaticBox(self, -1, "发散开口幅度(倍)")
        self.enlarge_scope_sizer = wx.StaticBoxSizer(self.enlarge_scope_box, wx.VERTICAL)
        self.enlarge_scope_cmbo = wx.ComboBox(self, -1, u"1.5", choices=["0", "1.1", "1.5", "2", "2.5"],
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择扩大倍数
        self.enlarge_scope_sizer.Add(self.enlarge_scope_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.first_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.second_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.third_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.fourth_average_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.continue_days_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.enlarge_scope_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizerAndFit(self.FlexGridSizer)
        self.Centre()

    def feedback_paras(self):

        self.raise_para = dict()
        self.raise_para[u"第一条均线周期"] = int(self.first_average_input.GetValue())
        self.raise_para[u"第二条均线周期"] = int(self.second_average_input.GetValue())
        self.raise_para[u"第三条均线周期"] = int(self.third_average_input.GetValue())
        self.raise_para[u"第四条均线周期"] = int(self.fourth_average_input.GetValue())
        self.raise_para[u"连续发散天数"] = int(self.continue_days_input.GetValue())
        self.raise_para[u"开口放大倍数"] = float(self.enlarge_scope_cmbo.GetStringSelection())
        return self.raise_para

class NeedleBottomDialog(wx.Dialog):  # 底部平台突破参数

    def __init__(self, parent, title=u"自定义提示信息", size=(500, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=3, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 单针探底的幅度(%)
        self.bottom_rate_box = wx.StaticBox(self, -1, "单针探底的幅度(%)")
        self.bottom_rate_sizer = wx.StaticBoxSizer(self.bottom_rate_box, wx.VERTICAL)
        self.bottom_rate_input = wx.TextCtrl(self, -1, "5", style=wx.TE_PROCESS_ENTER)
        self.bottom_rate_sizer.Add(self.bottom_rate_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 探底后回升的幅度(%)
        self.raise_rate_box = wx.StaticBox(self, -1, "探底后回升的幅度(%)")
        self.raise_rate_sizer = wx.StaticBoxSizer(self.raise_rate_box, wx.VERTICAL)
        self.raise_rate_input = wx.TextCtrl(self, -1, "3", style=wx.TE_PROCESS_ENTER)
        self.raise_rate_sizer.Add(self.raise_rate_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 近(N)日内出现单针信号
        self.occur_range_box = wx.StaticBox(self, -1, "近(N)日内出现单针信号")
        self.occur_range_sizer = wx.StaticBoxSizer(self.occur_range_box, wx.VERTICAL)
        self.occur_range_input = wx.TextCtrl(self, -1, "10", style=wx.TE_PROCESS_ENTER)
        self.occur_range_sizer.Add(self.occur_range_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 单针成交量是近(N)日内平均成交量的倍数
        self.volume_rate_box = wx.StaticBox(self, -1, "单针成交量是近(N)日内平均成交量的倍数")
        self.volume_rate_sizer = wx.StaticBoxSizer(self.volume_rate_box, wx.VERTICAL)
        self.volume_rate_input = wx.TextCtrl(self, -1, "1.5", style=wx.TE_PROCESS_ENTER)
        self.volume_rate_sizer.Add(self.volume_rate_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.bottom_rate_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.raise_rate_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.occur_range_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.volume_rate_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        self.needle_paras = dict()

        self.needle_paras[u"单针探底的幅度"] = float(self.bottom_rate_input.GetValue())
        self.needle_paras[u"探底后回升的幅度"] = float(self.raise_rate_input.GetValue())
        self.needle_paras[u"近N日内出现单针信号"] = int(self.occur_range_input.GetValue())
        self.needle_paras[u"单针成交量是近N日内平均成交量的倍数"] = float(self.volume_rate_input.GetValue())

        return self.needle_paras

class NewHighBreakDialog(wx.Dialog):

    def __init__(self, parent, title=u"自定义提示信息", size=(500, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 突破高点幅度下限(%)
        self.under_ratio_box = wx.StaticBox(self, -1, "突破高点幅度下限(%)")
        self.under_ratio_sizer = wx.StaticBoxSizer(self.under_ratio_box, wx.VERTICAL)
        self.under_ratio_input = wx.TextCtrl(self, -1, "95", style=wx.TE_PROCESS_ENTER)
        self.under_ratio_sizer.Add(self.under_ratio_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 突破高点幅度上限(%)
        self.above_ratio_box = wx.StaticBox(self, -1, "突破高点幅度上限(%)")
        self.above_ratio_sizer = wx.StaticBoxSizer(self.above_ratio_box, wx.VERTICAL)
        self.above_ratio_input = wx.TextCtrl(self, -1, "105", style=wx.TE_PROCESS_ENTER)
        self.above_ratio_sizer.Add(self.above_ratio_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 近期上涨趋势检测天数
        self.trend_range_box = wx.StaticBox(self, -1, "近期上涨趋势检测天数")
        self.trend_range_sizer = wx.StaticBoxSizer(self.trend_range_box, wx.VERTICAL)
        self.trend_range_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.trend_range_sizer.Add(self.trend_range_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 突破近(N)日内高点
        self.highest_range_box = wx.StaticBox(self, -1, "突破近(N)日内高点")
        self.highest_range_sizer = wx.StaticBoxSizer(self.highest_range_box, wx.VERTICAL)
        self.highest_range_input = wx.TextCtrl(self, -1, "120", style=wx.TE_PROCESS_ENTER)
        self.highest_range_sizer.Add(self.highest_range_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.under_ratio_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.above_ratio_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trend_range_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.highest_range_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        self.new_high_paras = dict()

        self.new_high_paras[u"突破高点幅度下限"] = float(self.under_ratio_input.GetValue())
        self.new_high_paras[u"突破高点幅度上限"] = float(self.above_ratio_input.GetValue())
        self.new_high_paras[u"近期上涨趋势检测天数"] = int(self.trend_range_input.GetValue())
        self.new_high_paras[u"突破近N日内高点"] = int(self.highest_range_input.GetValue())

        return self.new_high_paras

class RpsTopNDialog(wx.Dialog):  # RPS-10参数

    def __init__(self, parent, title=u"自定义提示信息", size=(250, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 选取显示的排名范围
        self.sel_order_box = wx.StaticBox(self, -1, "选择观测的排名范围")
        self.sel_order_sizer = wx.StaticBoxSizer(self.sel_order_box, wx.VERTICAL)
        self.sel_order_val = [u"前10", u"前20", u"前30", u"前40", u"前50"]
        self.sel_order_cmbo = wx.ComboBox(self, -1, u"前10", choices=self.sel_order_val,
                                            style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.sel_order_sizer.Add(self.sel_order_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.sel_order_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)
        self.Centre()

    def feedback_paras(self):

        self.rps_para = dict()
        self.rps_para[u"选取显示的排名范围"] = (int(self.sel_order_cmbo.GetSelection())+1)*10

        return self.rps_para

class RpsTrackDialog(wx.Dialog):  # 跟踪个股RPS走势

    def __init__(self, parent, title=u"自定义提示信息", track_name="", df_track=[], size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.track_name = track_name
        self.df_track = df_track

        self.TrackPanel = MergePanel(self)  # 自定义
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.TrackPanel, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.Centre()
        self.draw_figure()

    def draw_figure(self):

        """
        fig = plt.figure(figsize=(12, 8))
        # 在Figure对象中创建一个Axes对象，每个Axes对象即为一个绘图区域 
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        self.df_track['close'].plot(ax=ax1, color='r')
        ax1.set_title(self.track_name + '股价走势', fontsize=15)
        # ax = plt.gca()
        ax1.spines['right'].set_color('none')
        ax1.spines['top'].set_color('none')

        self.df_track['rps'].plot(ax=ax2, color='b')
        ax2.set_title(self.track_name + 'RPS相对强度', fontsize=15)
        my_ticks = pd.date_range(self.df_track.index[0], self.df_track.index[-1], freq='m')
        ax2.set_xticklabels(my_ticks)
        # ax = plt.gca()
        ax2.spines['right'].set_color('none')
        ax2.spines['top'].set_color('none')
        """
        self.TrackPanel.up_figure.clear()
        self.TrackPanel.down_figure.clear()

        self.df_track['close'].plot(ax=self.TrackPanel.up_figure)
        self.df_track['rps'].plot(ax=self.TrackPanel.down_figure)

        self.TrackPanel.up_figure.set_xlabel("")
        self.TrackPanel.up_figure.set_ylabel("股价走势")
        self.TrackPanel.up_figure.set_title(self.track_name)

        self.TrackPanel.down_figure.set_xlabel("日期")
        self.TrackPanel.down_figure.set_ylabel("RPS相对强度")
        self.TrackPanel.down_figure.set_title("")

        for label in self.TrackPanel.up_figure.xaxis.get_ticklabels():  # X-轴每个ticker标签隐藏
            label.set_visible(False)

        self.TrackPanel.FigureCanvas.draw()

class TradeConfDialog(wx.Dialog):  # 交易参数

    def __init__(self, parent, code="", name="", latest_close="", trade_price="", direct="买",  amount="100",
                                    title=u"自定义提示信息", size=(250, 500)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=10, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 股票代码
        self.stock_code_box = wx.StaticBox(self, -1, "股票代码")
        self.stcok_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stcok_code_input = wx.TextCtrl(self, -1, code, style=wx.TE_READONLY)
        self.stcok_code_sizer.Add(self.stcok_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 股票名称
        self.stock_name_box = wx.StaticBox(self, -1, "股票名称")
        self.stcok_name_sizer = wx.StaticBoxSizer(self.stock_name_box, wx.VERTICAL)
        self.stcok_name_input = wx.TextCtrl(self, -1, name, style=wx.TE_READONLY)
        self.stcok_name_sizer.Add(self.stcok_name_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 买或卖
        self.bs_direct_box = wx.StaticBox(self, -1, "买/卖")
        self.bs_direct_sizer = wx.StaticBoxSizer(self.bs_direct_box, wx.VERTICAL)
        self.bs_direct_val = [u"买", u"卖"]
        self.bs_direct_cmbo = wx.ComboBox(self, -1, direct, choices=self.bs_direct_val,
                                            style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.bs_direct_sizer.Add(self.bs_direct_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 最新价格
        self.latest_close_box = wx.StaticBox(self, -1, "最新价格")
        self.latest_close_sizer = wx.StaticBoxSizer(self.latest_close_box, wx.VERTICAL)
        self.latest_close_input = wx.TextCtrl(self, -1, str(latest_close), style=wx.TE_PROCESS_ENTER)
        self.latest_close_sizer.Add(self.latest_close_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 交易价格
        self.trade_price_box = wx.StaticBox(self, -1, "交易价格")
        self.trade_price_sizer = wx.StaticBoxSizer(self.trade_price_box, wx.VERTICAL)
        self.trade_price_input = wx.TextCtrl(self, -1, str(trade_price), style=wx.TE_PROCESS_ENTER)
        self.trade_price_sizer.Add(self.trade_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 数量
        self.trade_amount_box = wx.StaticBox(self, -1, "数量(股)")
        self.trade_amount_sizer = wx.StaticBoxSizer(self.trade_amount_box, wx.VERTICAL)
        self.trade_amount_input = wx.TextCtrl(self, -1, str(amount), style=wx.TE_PROCESS_ENTER)
        self.trade_amount_sizer.Add(self.trade_amount_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 策略跟踪
        self.trace_strategy_box = wx.StaticBox(self, -1, u'自定义策略跟踪')
        self.trace_strategy_sizer = wx.StaticBoxSizer(self.trace_strategy_box, wx.VERTICAL)
        self.trace_strategy_val = [u"自定义策略1", u"自定义策略2", u"自定义策略3"]
        self.trace_strategy_cmbo = wx.ComboBox(self, -1, u"自定义策略1", choices=self.trace_strategy_val,
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.trace_strategy_sizer.Add(self.trace_strategy_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 自动交易
        self.auto_trade_box = wx.StaticBox(self, -1, u'是否自动交易')
        self.auto_trade_sizer = wx.StaticBoxSizer(self.auto_trade_box, wx.HORIZONTAL)
        self.auto_trade_chk = wx.CheckBox(self, label='确定执行')
        self.auto_trade_chk.Bind(wx.EVT_CHECKBOX, self._ev_auto_trade)  # 绑定复选框事件
        self.auto_trade_sizer.Add(self.auto_trade_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.stcok_code_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stcok_name_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.bs_direct_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.latest_close_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trade_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trade_amount_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trace_strategy_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.auto_trade_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizerAndFit(self.FlexGridSizer)
        self.Centre()

    def _ev_auto_trade(self, event):

        print("执行自动交易请参考公众号文章部署环境！")

    def execute_paras(self):

        name = self.stcok_name_input.GetValue()
        self.trade_para = {name:{}}

        self.trade_para[name][u"code"] = self.stcok_code_input.GetValue()
        self.trade_para[name][u"direct"] = self.bs_direct_cmbo.GetStringSelection()
        self.trade_para[name][u"close"] = float(self.latest_close_input.GetValue())
        self.trade_para[name][u"price"] = float(self.trade_price_input.GetValue())
        self.trade_para[name][u"amount"] = int(self.trade_amount_input.GetValue())
        self.trade_para[name][u"trace_strategy"] = self.trace_strategy_cmbo.GetStringSelection()
        self.trade_para[name][u"auto_trade"] = self.auto_trade_chk.GetValue()

        return self.trade_para

class HoldConfDialog(wx.Dialog):  # 持有参数

    def __init__(self, parent, code="", name="", exceed=u"", retreat="", price="", highest="",
                                    title=u"自定义提示信息", size=(250, 700)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=12, cols=1, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 股票代码
        self.stock_code_box = wx.StaticBox(self, -1, "股票代码")
        self.stcok_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stcok_code_input = wx.TextCtrl(self, -1, code, style=wx.TE_READONLY)
        self.stcok_code_sizer.Add(self.stcok_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 股票名称
        self.stock_name_box = wx.StaticBox(self, -1, "股票名称")
        self.stcok_name_sizer = wx.StaticBoxSizer(self.stock_name_box, wx.VERTICAL)
        self.stcok_name_input = wx.TextCtrl(self, -1, name, style=wx.TE_READONLY)
        self.stcok_name_sizer.Add(self.stcok_name_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 止盈方式
        self.stop_profit_box = wx.StaticBox(self, -1, "止盈模式")
        self.stop_profit_sizer = wx.StaticBoxSizer(self.stop_profit_box, wx.VERTICAL)
        self.stop_profit_val = [u"固定比例"]
        self.stop_profit_cmbo = wx.ComboBox(self, -1, self.stop_profit_val[0], choices=self.stop_profit_val,
                                            style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.stop_profit_sizer.Add(self.stop_profit_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 止损方式
        self.stop_loss_box = wx.StaticBox(self, -1, "止损模式")
        self.stop_loss_sizer = wx.StaticBoxSizer(self.stop_loss_box, wx.VERTICAL)
        self.stop_loss_val = [u"回撤比例"]
        self.stop_loss_cmbo = wx.ComboBox(self, -1, self.stop_loss_val[0], choices=self.stop_loss_val,
                                            style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.stop_loss_sizer.Add(self.stop_loss_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 盈利百分比
        self.exceed_per_box = wx.StaticBox(self, -1, "盈利幅度%")
        self.exceed_per_sizer = wx.StaticBoxSizer(self.exceed_per_box, wx.VERTICAL)
        self.exceed_per_input = wx.TextCtrl(self, -1, str(exceed), style=wx.TE_PROCESS_ENTER)
        self.exceed_per_sizer.Add(self.exceed_per_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 回撤百分比
        self.retreat_per_box = wx.StaticBox(self, -1, "回撤幅度%")
        self.retreat_per_sizer = wx.StaticBoxSizer(self.retreat_per_box, wx.VERTICAL)
        self.retreat_per_input = wx.TextCtrl(self, -1, str(retreat), style=wx.TE_PROCESS_ENTER)
        self.retreat_per_sizer.Add(self.retreat_per_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 买入价格
        self.buy_price_box = wx.StaticBox(self, -1, "买入价格")
        self.buy_price_sizer = wx.StaticBoxSizer(self.buy_price_box, wx.VERTICAL)
        self.buy_price_input = wx.TextCtrl(self, -1, str(price), style=wx.TE_PROCESS_ENTER)
        self.buy_price_sizer.Add(self.buy_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 持有后最高价
        self.highest_price_box = wx.StaticBox(self, -1, "持有后最高价")
        self.highest_price_sizer = wx.StaticBoxSizer(self.highest_price_box, wx.VERTICAL)
        self.highest_price_input = wx.TextCtrl(self, -1, str(highest), style=wx.TE_PROCESS_ENTER)
        self.highest_price_sizer.Add(self.highest_price_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 策略跟踪
        self.trace_strategy_box = wx.StaticBox(self, -1, u'自定义策略跟踪')
        self.trace_strategy_sizer = wx.StaticBoxSizer(self.trace_strategy_box, wx.VERTICAL)
        self.trace_strategy_val = [u"自定义策略1", u"自定义策略2", u"自定义策略3"]
        self.trace_strategy_cmbo = wx.ComboBox(self, -1, u"自定义策略1", choices=self.trace_strategy_val,
                                          style=wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统
        self.trace_strategy_sizer.Add(self.trace_strategy_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 自动交易
        self.auto_trade_box = wx.StaticBox(self, -1, u'是否自动交易')
        self.auto_trade_sizer = wx.StaticBoxSizer(self.auto_trade_box, wx.HORIZONTAL)
        self.auto_trade_chk = wx.CheckBox(self, label='确定执行')
        self.auto_trade_chk.Bind(wx.EVT_CHECKBOX, self._ev_auto_trade)  # 绑定复选框事件
        self.auto_trade_sizer.Add(self.auto_trade_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.stcok_code_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stcok_name_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stop_profit_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stop_loss_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.exceed_per_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.retreat_per_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.buy_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.highest_price_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.trace_strategy_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.auto_trade_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def _ev_auto_trade(self, event):

        print("执行自动交易请参考公众号文章部署环境！")

    def execute_paras(self):

        name = self.stcok_name_input.GetValue()
        self.hold_para = {name:{}}

        self.hold_para[name][u"code"] = self.stcok_code_input.GetValue()
        self.hold_para[name][u"exceed"] = int(self.exceed_per_input.GetValue())
        self.hold_para[name][u"retreat"] = int(self.retreat_per_input.GetValue())
        self.hold_para[name][u"price"] = float(self.buy_price_input.GetValue())
        self.hold_para[name][u"highest"] = float(self.highest_price_input.GetValue())
        self.hold_para[name][u"trace_strategy"] = self.trace_strategy_cmbo.GetStringSelection()
        self.hold_para[name][u"auto_trade"] = self.auto_trade_chk.GetValue()

        return self.hold_para

class ViewGripDiag(wx.Dialog):

    def __init__(self, parent, title=u"表格数据显示", update_df=[], size=(750, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style = wx.DEFAULT_FRAME_STYLE)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.data_to_grid(update_df)

        sizer.Add(self.grid, flag=wx.ALIGN_CENTER)

        self.SetSizer(sizer)

    def data_to_grid(self, df):

        self.grid = wx.grid.Grid(self, -1)

        if df.empty != True:
            self.list_columns = df.columns.tolist()
            self.grid.CreateGrid(df.shape[0], df.shape[1]) # 初始化时默认生成

            for col, series in df.iteritems():  # 将DataFrame迭代为(列名, Series)对
                m = self.list_columns.index(col)
                self.grid.SetColLabelValue(m, col)
                for n, val in enumerate(series):
                    self.grid.SetCellValue(n, m, str(val))
                self.grid.AutoSizeColumn(m, True)  # 自动调整列尺寸

class CondSelDialog(wx.Dialog):  # 条件选股参数

    def __init__(self, parent, title=u"自定义提示信息", col_items=[], size=(500, 360)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 选股参数——条件表达式分析
        self.pick_stock_box = wx.StaticBox(self, -1, u'条件表达式选股')
        self.pick_stock_sizer = wx.StaticBoxSizer(self.pick_stock_box, wx.HORIZONTAL)

        self.pick_item_cmbo = wx.ComboBox(self, -1,  choices=col_items,
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项

        #self.pick_item_cmbo.Bind(wx.EVT_RADIOBUTTON, self._ev_items_choose)

        self.pick_cond_cmbo = wx.ComboBox(self, -1, u"大于",
                                          choices=[u"大于", u"等于", u"小于"],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股条件
        self.pick_value_text = wx.TextCtrl(self, -1, "0", style=wx.TE_LEFT)

        self.sort_values_cmbo = wx.ComboBox(self, -1, u"不排列",
                                            choices=[u"不排列", u"升序", u"降序"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 排列条件

        self.pick_stock_sizer.Add(self.pick_item_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_cond_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_value_text, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.sort_values_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 子参数——剔除ST/*ST 及 剔除科创板
        self.adv_select_box = wx.StaticBox(self, -1, u'勾选确认')
        self.adv_select_sizer = wx.StaticBoxSizer(self.adv_select_box, wx.HORIZONTAL)
        self.remove_st_chk = wx.CheckBox(self, label='剔除ST/*ST')
        self.remove_kc_chk = wx.CheckBox(self, label='剔除科创板')
        self.adv_select_sizer.Add(self.remove_st_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.adv_select_sizer.Add(self.remove_kc_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.pick_stock_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.adv_select_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizerAndFit(self.FlexGridSizer)
        self.Centre()

    def feedback_paras(self):

        self.cond_paras = dict()

        self.cond_paras[u"条件选项"] = self.pick_item_cmbo.GetStringSelection()
        self.cond_paras[u"条件符号"] = self.pick_cond_cmbo.GetStringSelection()
        self.cond_paras[u"条件值"] = self.pick_value_text.GetValue()
        self.cond_paras[u"结果排序"] = self.sort_values_cmbo.GetStringSelection()
        self.cond_paras[u"剔除ST"] = self.remove_st_chk.GetValue()
        self.cond_paras[u"剔除科创板"] = self.remove_kc_chk.GetValue()

        return self.cond_paras

class MsgInputDialog(wx.Dialog):  # 输入选股内容

    def __init__(self, parent, title=u"自定义提示信息", label=u"自定义日志", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.FlexGridSizer = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)

        # 输入选股条件
        self.sel_input_cbox = wx.ComboBox(self, -1, value='人气排行',
                                           choices=['当前热股', '今日涨停'],
                                           style=wx.CB_DROPDOWN)

        self.sel_cond_box = wx.StaticBox(self, -1, u'输入选股条件')
        self.sel_cond_sizer = wx.StaticBoxSizer(self.sel_cond_box, wx.VERTICAL)
        self.sel_cond_sizer.Add(self.sel_input_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 输入数据页数
        self.data_page_cbox = wx.ComboBox(self, -1, value="1", choices=["5", "10"],
                                           style=wx.CB_DROPDOWN)

        self.data_page_box = wx.StaticBox(self, -1, u'输入获取页数')
        self.data_page_sizer = wx.StaticBoxSizer(self.data_page_box, wx.VERTICAL)
        self.data_page_sizer.Add(self.data_page_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)


        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()

        # 加入Sizer中
        self.FlexGridSizer.Add(self.sel_cond_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.data_page_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        return self.sel_input_cbox.GetValue(),  int(self.data_page_cbox.GetValue()) # 返回选股条件


class DateInputDialog(wx.Dialog):  # 输入选股日期

    def __init__(self, parent, title=u"自定义提示信息", label=u"自定义日志", size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)

        # 选股参数——日历控件时间周期
        self.dpc_cur_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 当前时间

        self.cur_date_box = wx.StaticBox(self, -1, u'当前日期(Start)')
        self.cur_date_sizer = wx.StaticBoxSizer(self.cur_date_box, wx.VERTICAL)
        self.cur_date_sizer.Add(self.dpc_cur_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_cur_time.SetValue(date_time_now)
        # self.dpc_cur_time.SetValue(date_time_now.SetDay(9)) # 以9日为例 先不考虑周末的干扰

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()

        # 加入Sizer中
        self.FlexGridSizer.Add(self.cur_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        return self.dpc_cur_time.GetValue() # 输入选股日期

class IndustryCountDialog(wx.Dialog):  # 统计行业数目

    def __init__(self, parent, title=u"自定义提示信息", xlabel_str="", df_count=[], size=(800, 800)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.df_count = df_count
        self.xlabel = xlabel_str
        self.GroupPanel = GroupPanel(self)  # 自定义
        self.HBoxPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.HBoxPanelSizer.Add(self.GroupPanel, proportion=1, border=2, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.HBoxPanelSizer)  # 使布局有效
        self.draw_figure()

    def draw_figure(self):

        self.GroupPanel.relate.clear()
        self.df_count.plot.bar(ax=self.GroupPanel.relate)

        self.GroupPanel.relate.set_xlabel(self.xlabel)
        self.GroupPanel.relate.set_ylabel("涨停板数量")

        self.GroupPanel.FigureCanvas.draw()
