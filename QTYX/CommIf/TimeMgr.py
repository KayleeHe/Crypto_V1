#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

from datetime import datetime, timedelta

class TimeTrigger():

    def __init__(self, syslog_obj):

        self.syslog = syslog_obj

        cur_time = self.get_curtime
        # 设置开始时间为9:29
        self.start_time = datetime(cur_time.year, cur_time.month, cur_time.day, 9, 25)
        # 设置结束时间为15:01
        self.end_time = datetime(cur_time.year, cur_time.month, cur_time.day, 15, 1)
        #self.real_data_if = RealTimeData()

    @property
    def get_curtime(self):
        return datetime.now() # 当前时间

    def in_trade_time(self, cur_time):
        if ((cur_time > self.start_time) and (cur_time < self.start_time + timedelta(hours=2, minutes=2))) or \
                ((cur_time > self.end_time + timedelta(hours=-2, minutes=-2)) and (cur_time < self.end_time)):
            return True
        else:
            return False

    def before_trade_time(self, cur_time):

        if cur_time <= self.start_time:
            return True
        else:
            return False

    def after_trade_time(self, cur_time):
        if cur_time >= self.end_time:
            return True
        else:
            return False

    def trigger_once(self, MODE=False):
        """
        :param mode: True 表示盘后调试(手动条件当前时间模拟实盘调试); False 表示实盘运行
        :return:
        """
        self.syslog.re_print(u"启动时间触发程序......\n")

        if MODE == True:
            for hour in range(14, 15):
                for min in range(59, 60):
                    cur_time = datetime(2023, 8, 7, hour, min)  # 模拟实盘设置为当天日期
        else:
            cur_time = self.get_curtime # 实盘代码

        if self.in_trade_time(cur_time):
            # 9:25--11:31 12:59--15:01 时段获取数据
            self.syslog.re_print(u"当前时间{0}".format(cur_time.strftime("%Y-%m-%d_%H:%M:%S")))
            return True # 更新数据

        elif self.before_trade_time(cur_time):
            self.syslog.re_print(u"开始时间{0}--未开盘".format(self.start_time.strftime("%Y-%m-%d_%H:%M:%S")))
            return False
        elif self.after_trade_time(cur_time):
            self.syslog.re_print(u"结束时间{0}--已收盘".format(self.end_time.strftime("%Y-%m-%d_%H:%M:%S")))
            return False
        else:
            self.syslog.re_print(u"休息时间-- 11:30至13:00")
            return False
