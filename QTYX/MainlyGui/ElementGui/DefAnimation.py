#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import threading
import queue
import time
import wx
import random
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import mplfinance as mpf  # 替换 import mpl_finance as mpf

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

from MainlyGui.ElementGui.DefPanel import BasePanel, GroupPanel

# 正常显示画图时出现的中文和负号
from pylab import mpl
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

class KlineRunDialog(wx.Dialog):

    bars_range = 100 # 显示100个bars

    def __init__(self, parent, title=u"K线自动播放", update_df=[], size=(850, 800)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.SetBackgroundColour(wx.Colour('#EBEDEB'))

        self.disp_panel = BasePanel(self) # 自定义
        self.figure = self.disp_panel.figure
        self.ochl = self.disp_panel.ochl
        self.vol = self.disp_panel.vol

        self.start_btn = wx.Button(self, wx.ID_EXECUTE, u"开始")
        self.start_btn.Bind(wx.EVT_BUTTON, self.ev_start_move)  # 绑定按钮事件
        self.pause_btn = wx.Button(self, wx.ID_EXECUTE, u"暂停")
        self.pause_btn.Bind(wx.EVT_BUTTON, self.ev_pause_move)  # 绑定按钮事件
        self.stop_btn = wx.Button(self, wx.ID_EXECUTE, u"停止")
        self.stop_btn.Bind(wx.EVT_BUTTON, self.ev_stop_move)  # 绑定按钮事件

        self.cancel_btn = wx.Button(self, wx.ID_OK, u"取消")

        self.btns_Sizer = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        self.btns_Sizer.Add(self.start_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.pause_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.stop_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.cancel_btn, flag=wx.ALIGN_CENTER)

        self.vbox_sizer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_sizer.Add(self.disp_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox_sizer.Add(self.btns_Sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(self.vbox_sizer)
        self.Centre()
        self.Layout()
        #self.vbox_sizer.Fit(self)

        self.line, = self.ochl.plot([], [], '-', color='#239B3F', lw=1)

        self.st_dat = update_df

        self.animQueue = queue.Queue()

        # matplotlib.animation实现动画
        self.ani = animation.FuncAnimation(self.figure,
                                           self.animate,
                                           interval=1000,
                                           blit=False,
                                           init_func=self.init)

        # ani.save('jieky_animation.gif',writer='imagemagick')

        # 线程加载数据
        self.kill_flag = False

        # 动态数据通过队列和异步线程放入queue
        self.thread1 = threading.Thread(target=self.put_data_thread, args=(self.animQueue,))  # 添加线程
        self.thread1.start()
        self.Show()

    def ev_start_move(self, event):
        self.ani.event_source.start()
        self.pause_flag = False

    def ev_pause_move(self, event):
        self.ani.event_source.stop() # 动画停止
        self.pause_flag = True

    def ev_stop_move(self, event):
        self.stop_anim()

    def stop_anim(self):
        self.ani.event_source.stop()  # 动画停止
        self.kill_flag = True

    def put_data_thread(self, dummy):

        while True:
            for bar in self.st_dat.itertuples():
                time.sleep(0.5)
                while self.pause_flag == True: # 暂停
                    time.sleep(0.5)
                self.animQueue.put(bar)

                if self.kill_flag == True:
                    break
            break
        print("finish thread!")

    def init(self):

        # 常量
        self.initCount = 0
        self.pause_flag = True # 初始化时先暂停动画

        self.thisx = []
        self.thisy = []
        self.thisIndex = []
        self.thisOCHLV = pd.DataFrame()

        self.thisx = [i for i in range(0, self.bars_range+1)]
        self.thisy = (np.zeros(101, dtype=int) - 1).tolist()
        self.thisIndex = [id for id, _ in self.st_dat[0:self.bars_range+1].iterrows()]
        self.line.set_data([], [])
        # 设置x轴的范围
        self.ochl.set_xlim(min(self.thisx), max(self.thisx))
        # 更新刻度，刻度只要早x轴的范围内就可以
        self.ochl.set_xticks([i for i in range(min(self.thisx), max(self.thisx) + 1, 20)])
        # 设置刻度标签
        self.ochl.set_xticklabels(
            [i if i >= 0 else '' for i in range(min(self.thisx), max(self.thisx) + 1, 20)],
            rotation=0)
        return self.line

    def animate(self, *args):

        try:
            while not self.animQueue.empty():

                if self.pause_flag == True:
                    break

                bar = self.animQueue.get() # animation中取动态数据后, 重画图像。

                df_bar = pd.DataFrame({'Close': bar.Close, 'Open': bar.Open,
                              'High': bar.High,
                              'Low': bar.Low,
                              'Volume': bar.Volume}, index = [bar.Index])

                self.thisOCHLV = self.thisOCHLV.append(df_bar)

                # 清空重新绘制
                if bar.Close == -1:
                    self.initCount = 0
                    self.init()
                    continue
                else:
                    if self.initCount > self.bars_range:
                        del self.thisx[0]
                        del self.thisy[0]
                        self.thisx.append(max(self.thisx) + 1)
                        self.thisIndex.append(bar.Index)
                        self.thisy.append(bar.Close)
                    else:
                        self.thisx[self.initCount] = self.initCount
                        self.thisIndex.append(bar.Index)
                        self.thisy[self.initCount] = bar.Close
                        self.initCount += 1
        except:
            self.stop_anim()
            return

        if self.initCount > 0:

            self.ochl.set_xlim(min(self.thisx), max(self.thisx)) # 设置x轴的范围
            self.ochl.set_xticks([i for i in range(min(self.thisx), max(self.thisx) + 1, 20)]) # 更新x轴刻度

            self.vol.set_xlim(min(self.thisx), max(self.thisx)) # 设置x轴的范围
            self.vol.set_xticks([i for i in range(min(self.thisx), max(self.thisx) + 1, 20)]) # 更新x轴刻度

            self.vol.set_xticklabels(
                [self.thisIndex[i].strftime('%Y-%m-%d %H:%M') for i in range(min(self.thisx),
                                                    max(self.thisx) + 1, 20)], rotation=0) # 设置刻度标签

            for label in self.ochl.xaxis.get_ticklabels():  # X-轴每个ticker标签隐藏
                label.set_visible(False)
            for label in self.vol.xaxis.get_ticklabels():  # X-轴每个ticker标签隐藏
                label.set_rotation(15)  # X-轴每个ticker标签都向右倾斜15度
                label.set_fontsize(10)  # 设置标签字体

            # 重新渲染子图
            try:
                self.ochl.figure.canvas.draw()
            except:
                self.stop_anim()
                return

            # 绘制K线
            def_color = mpf.make_marketcolors(up='red', down='green', edge='black', wick='black')
            def_style = mpf.make_mpf_style(marketcolors=def_color, gridaxis='both', gridstyle='-.', y_on_right=False)
            mpf.plot(self.thisOCHLV, type='candle', style=def_style, ax=self.ochl)

            self.vol.bar(np.arange(0, len(self.thisOCHLV.index)), self.thisOCHLV.Volume,
                         color=['g' if self.thisOCHLV.Open[x] > self.thisOCHLV.Close[x]
                                else 'r' for x in range(0, len(self.thisOCHLV.index))])

            self.line.set_data(self.thisx, self.thisy)

        return self.line

class RpsCompeteDialog(wx.Dialog):

    bars_range = 100 # 显示100个bars
    players_num = 20 # 竞赛个股数量为10

    def __init__(self, parent, title=u"龙头股竞赛动画", update_df=[], size=(950, 900)):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_FRAME_STYLE)

        self.SetBackgroundColour(wx.Colour('#EBEDEB'))

        self.disp_panel = GroupPanel(self)  # 自定义
        self.figure = self.disp_panel.figure
        self.relate = self.disp_panel.relate

        self.start_btn = wx.Button(self, wx.ID_EXECUTE, u"开始")
        self.start_btn.Bind(wx.EVT_BUTTON, self.ev_start_move)  # 绑定按钮事件
        self.pause_btn = wx.Button(self, wx.ID_EXECUTE, u"暂停")
        self.pause_btn.Bind(wx.EVT_BUTTON, self.ev_pause_move)  # 绑定按钮事件
        self.stop_btn = wx.Button(self, wx.ID_EXECUTE, u"停止")
        self.stop_btn.Bind(wx.EVT_BUTTON, self.ev_stop_move)  # 绑定按钮事件
        self.cancel_btn = wx.Button(self, wx.ID_OK, u"取消")
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.ev_close_anim)  # 绑定按钮事件

        self.btns_Sizer = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        self.btns_Sizer.Add(self.start_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.pause_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.stop_btn, flag=wx.ALIGN_CENTER)
        self.btns_Sizer.Add(self.cancel_btn, flag=wx.ALIGN_CENTER)

        self.vbox_sizer = wx.BoxSizer(wx.VERTICAL)
        self.vbox_sizer.Add(self.disp_panel, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox_sizer.Add(self.btns_Sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(self.vbox_sizer)
        self.Centre()
        self.Layout()
        #self.vbox_sizer.Fit(self)

        self.pct_dat = np.round(((update_df / 100 + 1).cumprod() - 1) * 100, 2)

        shuffle_colors = ["#" + str(hex(col))[2:] for col in range(1048576, 9048576, 200)]

        random.shuffle(shuffle_colors)

        self.colors = dict(zip(self.pct_dat.columns.tolist(), shuffle_colors ))

        self.animQueue = queue.Queue()

        # matplotlib.animation实现动画, 让多幅图连续播放，每一幅图叫做一帧(frame)
        # fig：进行动画绘制的figure
        # func：更新函数
        # frames：传入更新函数的迭代值，即生成每一帧(frame)
        # init_func：初始函数
        # fargs：传入更新函数的额外参数
        # save_count：指定保存动画（gif或mp4）的帧数
        # interval：指定帧间隔时间，单位是ms
        # repeat_delay：如果指定了循环动画，则设置每次循环的间隔时间
        # repeat：指定是否循环动画
        # blit：是否优化绘图
        # cache_frame_data：控制是否缓存帧数据
        # 核心方法说明：
        # save(self, filename[, writer, fps, dpi, …])：将动画保存为文件（gif或mp4）.
        # to_html5_video(self[, embed_limit])：将动画HTML5动画
        # to_jshtml(self[, fps, embed_frames, …])：将动画返回为HTML格式

        self.ani = animation.FuncAnimation(self.figure,
                                           self.draw_barchart,
                                           interval=1000,
                                           blit=False,
                                           init_func=self._init)

        # ani.save('jieky_animation.gif',writer='imagemagick')

        # 线程加载数据
        self.kill_flag = False

        # 动态数据通过队列和异步线程放入queue
        self.thread1 = threading.Thread(target=self.put_data_thread, args=(self.animQueue,))  # 添加线程
        self.thread1.start()
        self.Show()

    def _init(self):
        self.pause_flag = True # 初始化时先暂停动画

    def ev_start_move(self, event):
        self.ani.event_source.start()
        self.pause_flag = False

    def ev_pause_move(self, event):
        self.ani.event_source.stop() # 动画停止
        self.pause_flag = True

    def ev_stop_move(self, event):
        self.stop_anim()

    def stop_anim(self):
        self.ani.event_source.stop()  # 动画停止
        self.kill_flag = True

    def ev_close_anim(self, event):
        self.stop_anim()
        self.Destroy()

    def put_data_thread(self, dummy):

        while True:
            for date, bars in self.pct_dat.iterrows():
                bars.sort_values(ascending=False, inplace=True)
                bars = bars[0:self.players_num]
                time.sleep(1)
                while self.pause_flag == True: # 暂停
                    time.sleep(1)

                self.animQueue.put((date, bars))

                if self.kill_flag == True:
                    break
            break
        print("finish thread!")

    def draw_barchart(self, *args):

        #try:
        while not self.animQueue.empty():
            if self.pause_flag == True:
                break

            bars = self.animQueue.get() # animation中取动态数据后, 重画图像。

            reverse_series = bars[1].reindex(bars[1].index[::-1])
            self.relate.clear()
            self.relate.barh(reverse_series.index, reverse_series.values, color=[self.colors[x] for x in reverse_series.index])

            dx = bars[1].values.max() / 200
            for i, (value, name) in enumerate(zip(reverse_series.values, reverse_series.index)):
                self.relate.text(value - dx, i, name, size=14, weight=600, ha='right', va='bottom')
                self.relate.text(value - dx, i - .25, self.colors[name], size=10, color='#444444', ha='right', va='baseline')
                self.relate.text(value + dx, i, f'{value:,.0f}', size=14, ha='left', va='center')
            # ... polished styles
            self.disp_panel.relate.text(1, 0.4, bars[0].strftime("%Y-%m-%d"), transform=self.relate.transAxes, color='#777777', size=46, ha='right', weight=800)
            self.relate.text(0, 1.06, '涨幅(%)', transform=self.relate.transAxes, size=12, color='#777777')
            self.relate.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
            self.relate.xaxis.set_ticks_position('top')
            self.relate.tick_params(axis='x', colors='#777777', labelsize=12)
            self.relate.set_yticks([])
            self.relate.margins(0, 0.01)
            self.relate.grid(which='major', axis='x', linestyle='-')
            self.relate.set_axisbelow(True)
            self.relate.text(0, 1.12, '哪只龙头股涨的最好, 买它就对了！',
                    transform=self.relate.transAxes, size=18, weight=600, ha='left')
            self.relate.text(1, 0, '全网唯一的功能就在QTYX中', transform=self.relate.transAxes, ha='right',
                    color='#777777', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
            plt.box(False)

            # 重新渲染子图
            self.figure.canvas.draw()

        #except:
        #    self.stop_anim()

        return
