#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx

class ClassifySelectDiag(wx.Dialog):

    def __init__(self, parent, title, map_table):
        super(ClassifySelectDiag, self).__init__(parent, title=title+"分类选择"+"(左边未选/右边已选)",
                                        size=(480, 500), style=wx.DEFAULT_FRAME_STYLE)

        #panel = wx.Panel(self)

        level_V1_box = wx.BoxSizer(wx.HORIZONTAL)

        self.info_desc_text = wx.StaticText(self, -1, u'关键字:')
        self.search_bk_input = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.search_btn = wx.Button(self, -1, u"搜索")

        self.okbtn = wx.Button(self, wx.ID_CANCEL, u"退出")
        self.okbtn.SetDefault()
        self.search_btn.Bind(wx.EVT_BUTTON, self._ev_search_run)  # 绑定按钮事件

        level_V1_box.Add(self.info_desc_text, proportion=1,flag=wx.EXPAND|wx.ALL, border=2)
        level_V1_box.Add(self.search_bk_input, proportion=2,flag=wx.EXPAND|wx.ALL, border=2)
        level_V1_box.Add(self.search_btn, proportion=1, flag=wx.EXPAND|wx.ALL, border=2)
        level_V1_box.Add(self.okbtn, proportion=1, flag=wx.EXPAND|wx.ALL, border=2)

        level_H1_box = wx.BoxSizer(wx.HORIZONTAL)
        self.map_table = map_table
        self.unselect = wx.ListBox(self, choices=list(self.map_table["未选择"].keys()), style=wx.LB_SINGLE)
        self.select = wx.ListBox(self, choices=list(self.map_table["已选择"].keys()), style=wx.LB_SINGLE)
        level_H1_box.Add(self.unselect, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        level_H1_box.Add(self.select, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)

        level_H2_box = wx.BoxSizer(wx.VERTICAL)
        level_H2_box.Add(level_V1_box, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        level_H2_box.Add(level_H1_box, proportion=7, flag=wx.EXPAND|wx.ALL, border=5)

        self.SetSizer(level_H2_box)
        self.Fit()

        self.Centre()
        self.Bind(wx.EVT_LISTBOX, self.onUnSelListBox, self.unselect)
        self.Bind(wx.EVT_LISTBOX, self.onSelListBox, self.select)
        self.Show(True)

    def onUnSelListBox(self, event):

        nameSelected = event.GetEventObject().GetStringSelection()
        indexSelected = event.GetEventObject().GetSelections()

        self.map_table["已选择"].update({nameSelected: self.map_table["未选择"][nameSelected]})
        self.map_table["未选择"].pop(nameSelected)
        self.unselect.Delete(indexSelected[0])
        self.select.InsertItems([nameSelected], 0)

    def onSelListBox(self, event):

        nameSelected = event.GetEventObject().GetStringSelection()
        indexSelected = event.GetEventObject().GetSelections()

        self.map_table["未选择"].update({nameSelected:self.map_table["已选择"][nameSelected]})
        self.map_table["已选择"].pop(nameSelected)
        self.select.Delete(indexSelected[0])
        self.unselect.InsertItems([nameSelected], 0)

    def _ev_search_run(self, event):  # 点击运行搜索

        bk_name = self.search_bk_input.GetValue()
        for key in self.map_table["未选择"].keys():
            if key.find(bk_name) != -1:
                self.unselect.SetFirstItem(key) # 把搜索的板块置顶

    def feedback_map(self):
        return self.map_table