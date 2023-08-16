#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import wx
import threading
import time


class ProgressBarDialog():

    def __init__(self, title=u"下载进度", init_len=1000):

        self.title = title
        self.message = "剩余时间"
        self.init_len = init_len
        self.dialog = wx.ProgressDialog(title=self.title, message=self.message, maximum=self.init_len,
                                        style=wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME)

    def update_bar(self, count):
        self.dialog.Update(count)

    def close_bar(self):
        self.dialog.Destroy()

    def reset_range(self, init_len=1000):
        self.dialog.SetRange(init_len)

class DownloadDataThread(threading.Thread):
    """ 下载行情数据进度条类 """

    def __init__(self, callback_func, queue, title="下载进度"):
        """
        :param parent:  主线程UI
        :param timer:  计时器
        """
        super(DownloadDataThread, self).__init__()  # 继承

        self.q_codes = queue
        self.init_len = self.q_codes.qsize() + 1
        self.dialog_obj = ProgressBarDialog(title, self.init_len)
        self.update_result = callback_func
        self.setDaemon(True)  # 设置为守护线程， 即子线程是守护进程，主线程结束子线程也随之结束。

    def run(self):

        while not self.q_codes.empty():
            q_size = self.q_codes.qsize()
            wx.CallAfter(self.dialog_obj.update_bar, self.init_len-q_size)  # 更新进度条进度
            time.sleep(0.5)

        wx.CallAfter(self.dialog_obj.close_bar) # destroy进度条
        wx.CallAfter(self.update_result)

