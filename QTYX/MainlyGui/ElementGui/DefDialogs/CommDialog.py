#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import os

def MessageDialog(info=u"我是对话框", title=u"温馨提示"):
    # 提示对话框
    # info:提示内容
    back_info = ""
    dlg_mesg = wx.MessageDialog(None, info, title,
                                wx.YES_NO | wx.ICON_INFORMATION)
    if dlg_mesg.ShowModal() == wx.ID_YES:
        back_info = "点击Yes"
    else:
        back_info = "点击No"
    dlg_mesg.Destroy()
    return back_info

def ChoiceDialog(info, choice):

    dlg_mesg = wx.SingleChoiceDialog(None, info, u"单选提示", choice)
    dlg_mesg.SetSelection(0)  # default selection

    if dlg_mesg.ShowModal() == wx.ID_OK:
        select = dlg_mesg.GetStringSelection()
    else:
        select = None
    dlg_mesg.Destroy()
    return select

def ImportFileDiag(path=None):
    # 导入文件对话框
    # return:文件路径
    # wildcard = "CSV Files (*.xls)|*.xls"
    wildcard = "CSV Files (*.csv)|*.csv"
    dlg_mesg = wx.FileDialog(
        None, "请选择文件", path, "", wildcard, wx.FD_OPEN | wx.FD_CHANGE_DIR
        | wx.FD_FILE_MUST_EXIST)  # 旧版 wx.OPEN wx.CHANGE_DIR
    if dlg_mesg.ShowModal() == wx.ID_OK:
        file_path = dlg_mesg.GetPath()
    else:
        file_path = ''
    dlg_mesg.Destroy()
    return file_path


class CheckBoxesDialog(wx.Dialog):  # check boxes 组合

    def __init__(self, parent, title=u"组合多选框", items=[], size=(700, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.FlexGridSizer = wx.FlexGridSizer(rows=len(items), cols=1, vgap=0, hgap=0)
        self.label_id_map = {}

        for label_para in items:
            self.label_id_map[label_para] = wx.NewId()
            sel_your_chk = wx.CheckBox(self, self.label_id_map[label_para], label=label_para)
            # 加入Sizer中
            self.FlexGridSizer.Add(sel_your_chk, proportion=1, border=1, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
        self.SetSizerAndFit(self.FlexGridSizer)

    def feedback_paras(self):

        values_id_map = []

        for label, id in self.label_id_map.items():
            val = wx.Window.FindWindowById(id).GetValue()
            if val == True: values_id_map.append(label)

        return values_id_map # 返回选择结果

