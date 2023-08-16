#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import numpy as np
import pandas as pd
import sqlite3

# 使用Python3自带的sqlite数据库
class DataBase_Sqlite(object):

    def __init__(self, db_name='stock-data.db'):
        self.conn = sqlite3.connect(db_name)

    def read_table(self, table_name='stock_profit_stock'):
        # 读取整张表数据
        df = pd.read_sql_query(f"select * from \'{table_name}\'", self.conn)
        return df

    def save_table(self, df, table_name):
        df.to_sql(name=table_name, con=self.conn, index=False,
                   # index_label='id',
                   if_exists='replace')

    def drop_table(self, table_name):
        # 删除一个表
        c = self.conn.cursor()
        c.execute("drop table "+ table_name)
        self.conn.commit()

    def close_base(self):
        # 关闭数据库
        self.conn.close()


