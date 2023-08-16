#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import threading
import time

class CrawlerThread(threading.Thread):
    """爬虫类"""
    def __init__(self, parent, queue_in, queue_out, taskif):

        super(CrawlerThread, self).__init__()
        self.parent = parent
        self.taskif = taskif
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.setDaemon(True)

    def run(self):

        while not self.queue_in.empty():
            para = self.queue_in.get()
            results = self.taskif(para)
            if self.queue_out.full() != True:
                self.queue_out.put(results)