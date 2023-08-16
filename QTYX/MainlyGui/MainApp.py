#! /usr/bin/env python 
#-*- encoding: utf-8 -*- 
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import wx.adv
import wx.grid
import wx.html2
import os

from MainlyGui.LoginFrame import LoginFrame
from MainlyGui.UserFrame import UserFrame

class GuiManager():
    def __init__(self, Fun_SwFrame):
        self.fun_swframe = Fun_SwFrame
        self.frameDict = {}  # 用来装载已经创建的Frame对象
        # hack to help on dual-screen, need something better XXX - idfah
        displaySize = wx.DisplaySize()  # (1920, 1080)
        MIN_DISPLAYSIZE = 1280, 1024
        if (displaySize[0] < MIN_DISPLAYSIZE[0]) or (MIN_DISPLAYSIZE[1] < 1024):
            self.MsgDialog(f"由于您的显示器分辨率过低(低于{MIN_DISPLAYSIZE[0]},{MIN_DISPLAYSIZE[1]})，会导致部分控件显示异常！\
                           请调整显示器设置的【缩放比例】及【分辨率】")
            self.displaySize = MIN_DISPLAYSIZE[0], MIN_DISPLAYSIZE[1]
        else:
            self.displaySize = 1280, 900

    def MsgDialog(self, info):
        # 提示一些使用注意事项的对话框
        dlg_mesg = wx.MessageDialog(None, info, u"温馨提示",
                                    wx.YES_NO | wx.ICON_INFORMATION)
        dlg_mesg.ShowModal()
        dlg_mesg.Destroy()

    def GetFrame(self, type):
        frame = self.frameDict.get(type)
        if frame is None:
            frame = self.ReturnFrame(type)
            self.frameDict[type] = frame
        return frame

    def ReturnFrame(self, type):

        if type == 0: # 主界面
            return LoginFrame(parent=None, id=type,
                             displaySize=self.displaySize, Fun_SwFrame=self.fun_swframe)
        elif type == 1: # 量化分析界面
            return UserFrame(parent=None, id=type,
                             displaySize=self.displaySize, Fun_SwFrame=self.fun_swframe)
        else:
            pass

class MainApp(wx.App):

    store_path = os.path.dirname(os.path.dirname(__file__))

    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.manager = GuiManager(self.SwitchFrame)
        self.frame = self.manager.GetFrame(0)
        self.frame.icon = wx.Icon(self.store_path+'/ConfigFiles/png/logo.ico', wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(self.frame.icon)
        self.frame.Show()
        self.frame.Center()
        self.SetTopWindow(self.frame)
        return True

    def SwitchFrame(self, type):
        # 切换Frame对象
        self.frame.Show(False)
        self.frame = self.manager.GetFrame(type)
        self.frame.icon = wx.Icon(self.store_path+'/ConfigFiles/png/logo.ico', wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(self.frame.icon)
        self.frame.Center()
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

    def OnExit(self):
        """
        for frame in self.manager.frameDict.values():
            frame.Close(True)
        self.ExitMainLoop()
        return 0
        """
        wx.Exit()