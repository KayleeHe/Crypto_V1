#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究
# 公众号: 元宵大师带你用Python量化交易

import wx
import platform

from CommIf.SysFile import Base_File_Oper

class LoginFrame(wx.Frame):

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):

        displaySize_shrink = 0.3*displaySize[0], 0.4*displaySize[1]

        wx.Frame.__init__(self, parent=None, title=u'登陆页面', size=displaySize_shrink, style=wx.DEFAULT_FRAME_STYLE)

        self.fun_swframe = Fun_SwFrame
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.sys_para = Base_File_Oper.load_sys_para("sys_para.json")
        self.ts_token = Base_File_Oper.read_tushare_token()

        sys_input_box = wx.StaticBox(self, -1, u'系统选项')
        sys_input_sizer = wx.StaticBoxSizer(sys_input_box, wx.VERTICAL)

        # 初始化操作系统类别
        # 获取系统信息 Windows系统下运行返回 'Windows'，Linux返回'Linux' MacOS返回'Darwin'
        operate_sys = platform.system()
        if operate_sys == 'Darwin':
            operate_sys = 'MacOS'
        sel_operate_text = wx.StaticText(self, -1, u'当前操作系统')
        sel_operate_text.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.sel_operate_cmbo = wx.ComboBox(self, -1, self.sys_para["operate_sys"],
                                          choices=[u"macos", u"windows"],
                                          style=wx.CB_SIMPLE | wx.CB_DROPDOWN | wx.CB_READONLY)  # 选择操作系统

        self.sel_operate_cmbo.SetStringSelection(operate_sys)
        # 设置tushare token码
        ts_token_text = wx.StaticText(self, -1, u'tushare token码\n'
                                                u'使用tushare接口获取股票代码表,未填写则会默认使用本地股票代码表！')
        ts_token_text.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.ts_token_tx = wx.TextCtrl(self, value=self.ts_token, style=wx.TE_MULTILINE,
                                       size=(int(displaySize_shrink[0]*0.9), int(displaySize_shrink[0]*0.3)))

        # 界面尺寸大小提示
        disp_size_text = wx.StaticText(self, -1, u'注意：\n'
                                                 u'当前显示器屏幕尺寸是(长:{};宽:{})\n'
                                                 u'可切换显示器分辨率来兼容显示效果！'.format(displaySize[0], displaySize[1]))
        disp_size_text.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))

        sys_input_sizer.Add(sel_operate_text, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        sys_input_sizer.Add(self.sel_operate_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        sys_input_sizer.Add(ts_token_text, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        sys_input_sizer.Add(self.ts_token_tx, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        sys_input_sizer.Add(disp_size_text, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)

        # 登陆按钮
        self.login_but = wx.Button(self, -1, "登陆")
        self.login_but.Bind(wx.EVT_BUTTON, self._ev_login)  # 绑定按钮事件

        # 退出按钮
        self.exit_but = wx.Button(self, -1, "退出")
        self.exit_but.Bind(wx.EVT_BUTTON, self._ev_exit)  # 绑定按钮事件

        # 创建FlexGridSizer布局网格
        # rows 定义GridSizer行数
        # cols 定义GridSizer列数
        # vgap 定义垂直方向上行间距
        # hgap 定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        self.FlexGridSizer.Add(self.login_but, proportion=1, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        self.FlexGridSizer.Add(self.exit_but, proportion=1, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        vboxnet = wx.BoxSizer(wx.VERTICAL)
        vboxnet.Add(sys_input_sizer, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)  # proportion参数控制容器尺寸比例
        vboxnet.Add(self.FlexGridSizer, proportion=0, flag=wx.EXPAND | wx.ALL| wx.CENTER, border=2)

        self.SetSizerAndFit(vboxnet)
        self.Center()

    def _ev_login(self, event):

        Base_File_Oper.write_tushare_token(self.ts_token_tx.GetValue())
        self.sys_para["operate_sys"] = self.sel_operate_cmbo.GetStringSelection()
        Base_File_Oper.save_sys_para("sys_para.json", self.sys_para)
        self.fun_swframe(1) # 进入量化界面

    def _ev_exit(self, event):
        #self.Close()
        wx.Exit()