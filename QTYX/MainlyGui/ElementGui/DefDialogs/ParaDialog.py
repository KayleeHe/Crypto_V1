#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
from datetime import datetime

class MarketGraphDialog(wx.Dialog):  # 行情走势图参数配置

    def __init__(self, parent, title=u"自定义提示信息", size=(800, 100)):

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

        # 行情参数——日历控件时间周期
        self.dpc_end_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间
        self.dpc_start_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#起始时间

        self.start_date_box = wx.StaticBox(self, -1, u'开始日期(Start)')
        self.end_date_box = wx.StaticBox(self, -1, u'结束日期(End)')
        self.start_date_sizer = wx.StaticBoxSizer(self.start_date_box, wx.VERTICAL)
        self.end_date_sizer = wx.StaticBoxSizer(self.end_date_box, wx.VERTICAL)
        self.start_date_sizer.Add(self.dpc_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.end_date_sizer.Add(self.dpc_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_end_time.SetValue(date_time_now)
        self.dpc_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 行情参数——股票周期选择
        self.stock_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.stock_period_sizer = wx.StaticBoxSizer(self.stock_period_box, wx.VERTICAL)
        self.stock_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.stock_period_cbox.SetSelection(2)
        self.stock_period_sizer.Add(self.stock_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——股票复权选择
        self.stock_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.stock_authority_sizer = wx.StaticBoxSizer(self.stock_authority_box, wx.VERTICAL)
        self.stock_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.stock_authority_cbox.SetSelection(2)
        self.stock_authority_sizer.Add(self.stock_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.start_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.end_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        self.SetSizer(self.FlexGridSizer)

    def feedback_paras(self):

        self.ochl_paras = dict()

        self.ochl_paras[u"股票周期"] = self.stock_period_cbox.GetStringSelection()
        self.ochl_paras[u"股票复权"] = self.stock_authority_cbox.GetStringSelection()
        self.ochl_paras[u"开始日期"] = self.dpc_start_time.GetValue()
        self.ochl_paras[u"结束日期"] = self.dpc_end_time.GetValue()

        return self.ochl_paras

class BacktGraphDialog(wx.Dialog):  # 行情走势图参数配置

    def __init__(self, parent, title=u"自定义提示信息", size=(600, 250)):

        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=3, cols=4, vgap=0, hgap=0)

        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 行情参数——日历控件时间周期
        self.dpc_end_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间
        self.dpc_start_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#起始时间

        self.start_date_box = wx.StaticBox(self, -1, u'开始日期(Start)')
        self.end_date_box = wx.StaticBox(self, -1, u'结束日期(End)')
        self.start_date_sizer = wx.StaticBoxSizer(self.start_date_box, wx.VERTICAL)
        self.end_date_sizer = wx.StaticBoxSizer(self.end_date_box, wx.VERTICAL)
        self.start_date_sizer.Add(self.dpc_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.end_date_sizer.Add(self.dpc_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_end_time.SetValue(date_time_now)
        self.dpc_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 行情参数——股票周期选择
        self.stock_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.stock_period_sizer = wx.StaticBoxSizer(self.stock_period_box, wx.VERTICAL)
        self.stock_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.stock_period_cbox.SetSelection(2)
        self.stock_period_sizer.Add(self.stock_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——股票复权选择
        self.stock_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.stock_authority_sizer = wx.StaticBoxSizer(self.stock_authority_box, wx.VERTICAL)
        self.stock_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.stock_authority_cbox.SetSelection(2)
        self.stock_authority_sizer.Add(self.stock_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_cash_box = wx.StaticBox(self, -1, u'初始资金')
        self.init_cash_sizer = wx.StaticBoxSizer(self.init_cash_box, wx.VERTICAL)
        self.init_cash_input = wx.TextCtrl(self, -1, "100000", style=wx.TE_LEFT)
        self.init_cash_sizer.Add(self.init_cash_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_stake_box = wx.StaticBox(self, -1, u'交易规模')
        self.init_stake_sizer = wx.StaticBoxSizer(self.init_stake_box, wx.VERTICAL)
        self.init_stake_input = wx.TextCtrl(self, -1, "all", style=wx.TE_LEFT)
        self.init_stake_sizer.Add(self.init_stake_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_slippage_box = wx.StaticBox(self, -1, u'滑点')
        self.init_slippage_sizer = wx.StaticBoxSizer(self.init_slippage_box, wx.VERTICAL)
        self.init_slippage_input = wx.TextCtrl(self, -1, "0.01", style=wx.TE_LEFT)
        self.init_slippage_sizer.Add(self.init_slippage_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_commission_box = wx.StaticBox(self, -1, u'手续费')
        self.init_commission_sizer = wx.StaticBoxSizer(self.init_commission_box, wx.VERTICAL)
        self.init_commission_input = wx.TextCtrl(self, -1, "0.0005", style=wx.TE_LEFT)
        self.init_commission_sizer.Add(self.init_commission_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_tax_box = wx.StaticBox(self, -1, u'印花税')
        self.init_tax_sizer = wx.StaticBoxSizer(self.init_tax_box, wx.VERTICAL)
        self.init_tax_input = wx.TextCtrl(self, -1, "0.001", style=wx.TE_LEFT)
        self.init_tax_sizer.Add(self.init_tax_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.start_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.end_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.stock_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.Add(self.init_cash_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_stake_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_slippage_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.init_commission_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.Add(self.init_tax_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizer(self.FlexGridSizer)

    def feedback_paras(self):

        self.ochl_paras = dict()

        self.ochl_paras[u"股票周期"] = self.stock_period_cbox.GetStringSelection()
        self.ochl_paras[u"股票复权"] = self.stock_authority_cbox.GetStringSelection()
        self.ochl_paras[u"开始日期"] = self.dpc_start_time.GetValue()
        self.ochl_paras[u"结束日期"] = self.dpc_end_time.GetValue()
        self.ochl_paras[u"初始资金"] = self.init_cash_input.GetValue()
        self.ochl_paras[u"交易规模"] = self.init_stake_input.GetValue()
        self.ochl_paras[u"滑点"] = self.init_slippage_input.GetValue()
        self.ochl_paras[u"手续费"] = self.init_commission_input.GetValue()
        self.ochl_paras[u"印花税"] = self.init_tax_input.GetValue()

        return self.ochl_paras

class SelectModeDialog(wx.Dialog): # 形态选股参数/更新行情数据参数/RPS选股参数

    def __init__(self, parent,  title=u"形态选股参数配置", size=(750, 200)):

        self.spy_title = title

        if title == u"RPS选股参数配置":
            title = title + "-注意：过滤次新股/剔除ST/股票池范围,已经在数据更新时确定"

        wx.Dialog.__init__(self, parent, -1, title,
                           size=size, style=wx.DEFAULT_FRAME_STYLE)

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        if self.spy_title == u"更新数据参数配置":
            self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
            self.update_dialog(self.FlexGridSizer)
        elif self.spy_title == u"形态选股参数配置":
            self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=5, vgap=0, hgap=0)
            self.update_dialog(self.FlexGridSizer)
            self.patten_dialog(self.FlexGridSizer)
        elif self.spy_title == u"RPS选股参数配置":
            self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
            self.rps_dialog(self.FlexGridSizer)
        elif self.spy_title == u"个股RPS跟踪参数配置":
            self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
            self.track_dialog(self.FlexGridSizer)
        else:
            pass
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def update_dialog(self, sizer_object):

        # 过滤次新股
        self.filter_list_time = wx.adv.DatePickerCtrl(self, -1,
                                                  style = wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE)#结束时间

        self.filter_list_box = wx.StaticBox(self, -1, u'上市时间\n(过滤该时间之后上市的股票)')
        self.filter_list_sizer = wx.StaticBoxSizer(self.filter_list_box, wx.VERTICAL)
        self.filter_list_sizer.Add(self.filter_list_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.filter_list_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 剔除ST/*ST
        self.adv_select_box = wx.StaticBox(self, -1, u'勾选确认')
        self.adv_select_sizer = wx.StaticBoxSizer(self.adv_select_box, wx.HORIZONTAL)
        self.remove_st_chk = wx.CheckBox(self, label='剔除ST/*ST')
        self.remove_st_chk.SetValue(True)
        self.adv_select_sizer.Add(self.remove_st_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 股票池
        self.patten_pool_box = wx.StaticBox(self, -1, u'股票池')
        self.patten_pool_sizer = wx.StaticBoxSizer(self.patten_pool_box, wx.VERTICAL)
        self.patten_pool_cbox = wx.ComboBox(self, -1, u"", choices=[u"全市场股票", u"自选股票池", u"概念板块池", u"行业板块池"])
        self.patten_pool_cbox.SetSelection(0)
        self.patten_pool_sizer.Add(self.patten_pool_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 按钮确认和取消
        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 加入Sizer中
        # 第一排
        sizer_object.Add(self.filter_list_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.adv_select_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.patten_pool_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

    def patten_dialog(self, sizer_object):

        # 形态选股参数——日历控件时间周期
        self.patten_select_time = wx.adv.DatePickerCtrl(self, -1,
                                                        style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 结束时间

        self.patten_select_date_box = wx.StaticBox(self, -1, u' 选股日期(End)')
        self.patten_select_date_sizer = wx.StaticBoxSizer(self.patten_select_date_box, wx.VERTICAL)
        self.patten_select_date_sizer.Add(self.patten_select_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                          border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.patten_select_time.SetValue(date_time_now)

        # 选股结果叠加
        self.add_extra_box = wx.StaticBox(self, -1, u'叠加分析数据')
        self.add_extra_sizer = wx.StaticBoxSizer(self.add_extra_box, wx.HORIZONTAL)
        self.profit_report_chk = wx.CheckBox(self, label='季度利润报表')
        self.north_money_chk = wx.CheckBox(self, label='北向资金持股')
        self.fund_hold_chk = wx.CheckBox(self, label='季度基金持仓-预留')
        self.daily_basic_chk = wx.CheckBox(self, label='每日基本面指标')

        self.add_extra_sizer.Add(self.profit_report_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)
        self.add_extra_sizer.Add(self.north_money_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)
        self.add_extra_sizer.Add(self.fund_hold_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)
        self.add_extra_sizer.Add(self.daily_basic_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=1)

        # 形态选股参数——股票周期选择
        self.patten_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.patten_period_sizer = wx.StaticBoxSizer(self.patten_period_box, wx.VERTICAL)
        self.patten_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"日线"])
        self.patten_period_cbox.SetSelection(0)
        self.patten_period_sizer.Add(self.patten_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                     border=2)

        # 形态选股参数——股票复权选择
        self.patten_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.patten_authority_sizer = wx.StaticBoxSizer(self.patten_authority_box, wx.VERTICAL)
        self.patten_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.patten_authority_cbox.SetSelection(0)
        self.patten_authority_sizer.Add(self.patten_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                        border=2)

        # 形态选股参数———形态类型选取
        self.patten_type_box = wx.StaticBox(self, -1, u'选股模型')
        self.patten_type_sizer = wx.StaticBoxSizer(self.patten_type_box, wx.HORIZONTAL)

        self.patten_type_cmbo = wx.ComboBox(self, -1, choices=["双底形态突破", "箱体形态突破", "均线多头排列", "单针探底回升", "突破前期高点",
                                                               "跳空缺口-预留", "线性回归-预留"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项
        self.patten_type_cmbo.SetSelection(0)
        self.patten_type_sizer.Add(self.patten_type_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        sizer_object.Add(self.patten_select_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.add_extra_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.patten_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.patten_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.patten_type_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

    def rps_dialog(self, sizer_object):

        # RPS选股参数——日历控件时间周期
        self.rps_start_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 开始时间

        self.rps_start_date_box = wx.StaticBox(self, -1, u' 开始日期(Start)')
        self.rps_start_date_sizer = wx.StaticBoxSizer(self.rps_start_date_box, wx.VERTICAL)
        self.rps_start_date_sizer.Add(self.rps_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                          border=2)

        # RPS选股参数——日历控件时间周期
        self.rps_select_time = wx.adv.DatePickerCtrl(self, -1,
                                                    style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 结束时间

        self.rps_select_date_box = wx.StaticBox(self, -1, u' 选股日期(End)')
        self.rps_select_date_sizer = wx.StaticBoxSizer(self.rps_select_date_box, wx.VERTICAL)
        self.rps_select_date_sizer.Add(self.rps_select_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                          border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.rps_select_time.SetValue(date_time_now)
        self.rps_start_time.SetValue(date_time_now)

        # RPS选股参数———形态类型选取
        self.rps_type_box = wx.StaticBox(self, -1, u'选股模型')
        self.rps_type_sizer = wx.StaticBoxSizer(self.rps_type_box, wx.HORIZONTAL)

        self.rps_type_cmbo = wx.ComboBox(self, -1, choices=["个股历史RPS排名", "板块历史RPS排名-预留"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项
        self.rps_type_cmbo.SetSelection(0)
        self.rps_type_sizer.Add(self.rps_type_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 选取涨跌幅滚动周期
        self.period_roll_box = wx.StaticBox(self, -1, "选取涨跌幅滚动周期")
        self.period_roll_sizer = wx.StaticBoxSizer(self.period_roll_box, wx.VERTICAL)
        self.period_roll_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.period_roll_sizer.Add(self.period_roll_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 按钮确认和取消
        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        # 加入Sizer中
        # 第二排
        sizer_object.Add(self.rps_start_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.rps_select_date_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.period_roll_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.rps_type_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

    def track_dialog(self, sizer_object):

        # 形态选股参数——股票周期选择
        self.patten_period_box = wx.StaticBox(self, -1, u'股票周期')
        self.patten_period_sizer = wx.StaticBoxSizer(self.patten_period_box, wx.VERTICAL)
        self.patten_period_cbox = wx.ComboBox(self, -1, u"", choices=[u"日线"])
        self.patten_period_cbox.SetSelection(0)
        self.patten_period_sizer.Add(self.patten_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                     border=2)

        # 形态选股参数——股票复权选择
        self.patten_authority_box = wx.StaticBox(self, -1, u'股票复权')
        self.patten_authority_sizer = wx.StaticBoxSizer(self.patten_authority_box, wx.VERTICAL)
        self.patten_authority_cbox = wx.ComboBox(self, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.patten_authority_cbox.SetSelection(0)
        self.patten_authority_sizer.Add(self.patten_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                        border=2)

        # 选取涨跌幅滚动周期
        self.period_roll_box = wx.StaticBox(self, -1, "选取涨跌幅滚动周期")
        self.period_roll_sizer = wx.StaticBoxSizer(self.period_roll_box, wx.VERTICAL)
        self.period_roll_input = wx.TextCtrl(self, -1, "20", style=wx.TE_PROCESS_ENTER)
        self.period_roll_sizer.Add(self.period_roll_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 按钮确认和取消
        self.ok_btn = wx.Button(self, wx.ID_OK, u"确认")
        self.ok_btn.SetDefault()
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, u"取消")

        sizer_object.Add(self.patten_period_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.patten_authority_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.period_roll_sizer, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.ok_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        sizer_object.Add(self.cancel_btn, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)

    def feedback_paras(self):

        self.patten_paras = dict()

        # 收集控件中设置的选项
        ##########################
        if self.spy_title ==  u"更新数据参数配置":
            filter_obj = self.filter_list_time.GetValue()
            filter_val = datetime(filter_obj.year, filter_obj.month + 1, filter_obj.day)
            self.patten_paras[u"过滤次新股上市时间"] = int(filter_val.strftime('%Y%m%d'))
            self.patten_paras[u"剔除ST股票"] = self.remove_st_chk.GetValue()
            self.patten_paras[u"股票池"] = self.patten_pool_cbox.GetStringSelection()
        elif self.spy_title ==  u"形态选股参数配置":
            filter_obj = self.filter_list_time.GetValue()
            filter_val = datetime(filter_obj.year, filter_obj.month + 1, filter_obj.day)
            self.patten_paras[u"过滤次新股上市时间"] = int(filter_val.strftime('%Y%m%d'))
            self.patten_paras[u"剔除ST股票"] = self.remove_st_chk.GetValue()
            self.patten_paras[u"股票池"] = self.patten_pool_cbox.GetStringSelection()
            self.patten_paras[u"选股日期"] = self.patten_select_time.GetValue()
            self.patten_paras[u"股票周期"] = self.patten_period_cbox.GetStringSelection()
            self.patten_paras[u"股票复权"] = self.patten_authority_cbox.GetStringSelection()
            self.patten_paras[u"选股模型"] = self.patten_type_cmbo.GetStringSelection()
            self.patten_paras[u"叠加利润报表"] = self.profit_report_chk.GetValue()
            self.patten_paras[u"北向资金持股"] = self.north_money_chk.GetValue()
            self.patten_paras[u"每日基本面指标"] = self.daily_basic_chk.GetValue()
        elif self.spy_title ==  u"RPS选股参数配置":
            # 收集控件中设置的选项
            self.patten_paras[u"开始日期"] = self.rps_start_time.GetValue()
            self.patten_paras[u"选股日期"] = self.rps_select_time.GetValue()
            self.patten_paras[u"选股模型"] = self.rps_type_cmbo.GetStringSelection()
            self.patten_paras[u"选取涨跌幅滚动周期"] = int(self.period_roll_input.GetValue())
        elif self.spy_title == u"个股RPS跟踪参数配置":
            # 收集控件中设置的选项
            self.patten_paras[u"股票周期"] = self.patten_period_cbox.GetStringSelection()
            self.patten_paras[u"股票复权"] = self.patten_authority_cbox.GetStringSelection()
            self.patten_paras[u"选取涨跌幅滚动周期"] = int(self.period_roll_input.GetValue())
        else:
            pass
        return self.patten_paras
