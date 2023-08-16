#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx

class ViewListDiag(wx.Dialog):

    def __init__(self, parent, title=u"表格数据显示", update_df=[], size=(1200, 500)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style = wx.DEFAULT_FRAME_STYLE)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT, size=size)

        update_df.insert(0, u"股票代码", update_df.index)

        for id, col in enumerate(update_df.columns):
            self.list.InsertColumn(id, col, wx.LIST_FORMAT_CENTRE, 90)

        for index, item in update_df.iterrows():
            row_id = self.list.InsertItem(90, str(item["股票代码"]))
            for col_id, col in enumerate(update_df.columns):
                if col != "股票代码":
                    self.list.SetItem(row_id, col_id, str(item[col]))

        sizer.Add(self.list, flag=wx.ALIGN_CENTER)

        self.SetSizer(sizer)

