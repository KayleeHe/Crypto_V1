#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

import time
import numpy as np
import pandas as pd
import datetime

class Base_Patten_Group():

    @staticmethod
    def double_bottom_search(name, code, stock_data, patlog_obj, **kwargs):
        """
        :param name:
        :param code:
        :param edate_val:
        :param stock_data:
        :param patlog_obj: 只打印符合条件的股票信息, 否则信息太多
        :param kwargs:
        :return:
        """
        # stock_data的数据格式 索引为'%Y-%m-%d'格式
        DOUBOT_DETECT_DATES_RANGE = kwargs["选取K线范围"]  # 往前寻找的范围 默认40
        DOUBOT_DETECT_DATES_MID = int(kwargs["选取K线范围"]/2)  # 区间划分中间点 默认40/2
        DOUBOT_DETECT_DATES_VAR = kwargs["选取中间区域误差"]  # 可变区间 默认 5

        DOUBOT_MIN_DIFF_FACTOR = kwargs["双底低点之间误差"]/100  # 最小值误差 默认0.03
        DOUBOT_BREAK_PCTCHG_VAR = kwargs["有效突破当天涨跌幅"]/100    # 有效突破当天涨跌幅 默认0.03
        DOUBOT_BREAK_RATIO_FACTOR = kwargs["有效突破颈线幅度"]/100  # 有效突破颈线幅度 默认 0.03
        DOUBOT_BREAK_VOLUME_THR = kwargs["有效突破成交量阈值"]/100  # 放量突破比例 默认超过平均的20%
        #DOUBOT_BREAK_BACKTEST_THR = kwargs["双底回测使能所需交易日"] # 放量突破比例 默认40个交易日
        DOUBOT_SVAE_MODE = kwargs["选股结果保存"] # "满足首次突破才保存"/"满足突破幅度就保存"

        df_result = pd.DataFrame(index=[0], columns=["股票名称", "股票代码", "识别日期",
                                                     "左底id", "左底价格", "右底id", "右底价格", "中顶id", "颈线价格",
                                                     "收盘价格", "首次突破", "当日涨幅",
                                                     "突破放量", "当前成交量(手)", "平均成交量(手)"])
        """
        recon_data = {'High': stock_data["最高价"], 'Low': stock_data["最低价"], 'Open': stock_data["开盘价"],
                      'Close': stock_data["收盘价"], 'Volume': stock_data["成交量"], 'pctChg': stock_data["涨跌幅"]}
        stock_data = pd.DataFrame(recon_data)
        """
        try:

            if len(stock_data) == 0: # 无行情数据则退出
                print(name, code, "data file length below 0")
                return pd.DataFrame()

            curdate_val = stock_data.index[-1]
            contain_log = ""

            # K线区间划分成两个子区间
            data_range1 = stock_data[
                          -DOUBOT_DETECT_DATES_RANGE: -(DOUBOT_DETECT_DATES_MID - DOUBOT_DETECT_DATES_VAR)]
            data_range2 = stock_data[-(DOUBOT_DETECT_DATES_MID + DOUBOT_DETECT_DATES_VAR):]

            # 计算K线区间成交量平均值(手)
            range_mean_vol_val = stock_data[-DOUBOT_DETECT_DATES_RANGE:-1]["成交量"].mean()

            # 分别计算子区间内收盘价最小值及出现日期
            range1_min_close_val = data_range1["收盘价"].min()
            range2_min_close_val = data_range2["收盘价"].min()
            range1_min_close_id = data_range1["收盘价"].idxmin()
            range2_min_close_id = data_range2["收盘价"].idxmin()

            # 分别计算子区间最小值之间的最大值及出现日期
            data_range_between = stock_data.loc[range1_min_close_id:range2_min_close_id]
            between_max_close_val = data_range_between["收盘价"].max()
            between_max_close_id = data_range_between["收盘价"].idxmax()

            # 选取双底两个低点中的较小值并计算两个低点的误差比例
            relative_min = range2_min_close_val if range1_min_close_val >= range2_min_close_val else range1_min_close_val
            error_ratio = np.abs(range1_min_close_val - range2_min_close_val) / relative_min

            # contain_log += "\n---分割线---\n"
            #contain_log += "数据最新日期 {}%; 控件选取识别日期 {}\n".format(curdate_val, edate_val)

            # 判断
            if (error_ratio <= DOUBOT_MIN_DIFF_FACTOR) and (range1_min_close_id != range2_min_close_id):

                # 选取当前交易日的收盘价和成交量
                current_time_val = stock_data.index[-1]
                current_close_val = stock_data["收盘价"][-1]
                current_volume_val = stock_data["成交量"][-1]
                current_pctchg_val = round(stock_data["涨跌幅"][-1], 4)

                # 计算有效突破颈线的价格, 包含了有效突破幅度值
                effective_break_value = between_max_close_val * (1 + DOUBOT_BREAK_RATIO_FACTOR)

                # 选取第二个最低点到当前日期大于有效突破值的天数
                from_min2_to_cur = stock_data.loc[range2_min_close_id:current_time_val]
                effective_break_df = from_min2_to_cur.loc[from_min2_to_cur["收盘价"] > effective_break_value]

                if current_close_val > effective_break_value:

                    contain_log += "[形态有效]: 股票{}, 代码{} 分析结果如下：\n".format(name, code)
                    contain_log += "  双底形态判断有效：左底 {}/{}元; 右底 {}/{}元; 中顶 {}/{}元;\n".format(
                        range1_min_close_id.strftime("%Y-%m-%d"),
                        np.round(range1_min_close_val, 2),
                        range2_min_close_id.strftime("%Y-%m-%d"),
                        np.round(range2_min_close_val, 2),
                        between_max_close_id.strftime("%Y-%m-%d"),
                        np.round(between_max_close_val, 2))

                    contain_log += "  双底形态突破幅度有效：当前收盘价 {}元; 颈线价格 {}元;\n".format(
                                                        current_close_val, np.round(between_max_close_val, 2))

                    df_result.loc[0, "股票名称"] = name
                    df_result.loc[0, "股票代码"] = code
                    df_result.loc[0, "识别日期"] = curdate_val.strftime("%Y-%m-%d")
                    df_result.loc[0, "左底id"] = range1_min_close_id.strftime("%Y-%m-%d")
                    df_result.loc[0, "左底价格"] = np.round(range1_min_close_val, 2)
                    df_result.loc[0, "右底id"] = range2_min_close_id.strftime("%Y-%m-%d")
                    df_result.loc[0, "右底价格"] = np.round(range2_min_close_val, 2)
                    df_result.loc[0, "中顶id"] = between_max_close_id.strftime("%Y-%m-%d")
                    df_result.loc[0, "颈线价格"] = np.round(between_max_close_val, 2)
                    df_result.loc[0, "收盘价格"] = np.round(current_close_val, 2)

                    if len(effective_break_df) == 1:
                        contain_log += "  当日为首次突破！！！\n"

                        df_result.loc[0, "首次突破"] = "Yes"

                        if current_pctchg_val >= DOUBOT_BREAK_PCTCHG_VAR:
                            contain_log += "  双底形态突破涨幅有效：当前涨幅 {}%;\n".format(current_pctchg_val)
                            df_result.loc[0, "涨幅有效"] = "Yes"
                            df_result.loc[0, "当日涨幅"] = current_pctchg_val

                            if (current_volume_val-range_mean_vol_val)/range_mean_vol_val >= DOUBOT_BREAK_VOLUME_THR: # 成交量放量突破判断
                                contain_log += "  双底形态突破放量有效：当前成交量 {}手; 平均成交量 {}手; \n".format(
                                                current_volume_val, range_mean_vol_val)
                                df_result.loc[0, "突破放量"] = "Yes"
                                df_result.loc[0, "当前成交量(手)"] = current_volume_val
                                df_result.loc[0, "平均成交量(手)"] = range_mean_vol_val
                            else:
                                contain_log += "  未形成有效突破放量！\n"
                                df_result.loc[0, "突破放量"] = "No"
                    else:
                        contain_log += "  非首次突破日！\n"
                        df_result.loc[0, "首次突破"] = "No"

                        if DOUBOT_SVAE_MODE == "满足首次突破才保存":return pd.DataFrame()

                    # if (curdate_val - edate_val) > datetime.timedelta(days=DOUBOT_BREAK_BACKTEST_THR):
                    #     contain_log += "  开启回测模式, 计算从形态突破日到当前交易日最大涨幅及最大亏损\n"
                    #     # 从识别到形态突破日期之后到当前交易日最大涨幅及最大亏损计算
                    #     back_min_close_val = back_data["Close"].min()
                    #     back_max_close_val = back_data["Close"].max()
                    #     back_min_close_id = back_data["Close"].idxmin()
                    #     back_max_close_id = back_data["Close"].idxmax()
                    #
                    #     profit_per = round(((back_max_close_val - current_close_val)/current_close_val*100) if back_max_close_val > current_close_val else 0, 2)
                    #     loss_per = round(((back_min_close_val - current_close_val)/current_close_val*100) if current_close_val > back_min_close_val else 0, 2)
                    #
                    #     df_result.loc[0, "最大盈利id"] = back_max_close_id
                    #     df_result.loc[0, "最大盈利价格"] = back_max_close_val
                    #     df_result.loc[0, "最大盈利比例%"] = profit_per
                    #     df_result.loc[0, "最大亏损id"] = back_min_close_id
                    #     df_result.loc[0, "最大亏损价格"] = back_min_close_val
                    #     df_result.loc[0, "最大亏损比例%"] = loss_per
                else:
                    # contain_log += "  未形成有效突破幅度！\n"
                    return pd.DataFrame()

            else:
                # contain_log += "形态无效: 滤除股票 {},代码 {}\n".format(name, code)
                return pd.DataFrame()

        except Exception as e:
            print(name, code, e)
            # contain_log += "股票 {},代码 {} 形态识别异常！可去除代码中的 try except 分析具体原因\n".format(name, code)

        if contain_log != '': patlog_obj.re_print(contain_log)

        return df_result

    @staticmethod
    def bottom_average_break(name, code, stock_data, patlog_obj, **kwargs):
        # 底部盘整，均线粘合，单阳突破 通达信公式
        # 股价在M日均线上下波动不超过15%，20日、30日、60日、120日均线收敛，当日涨幅超过5%且股价创M日新高
        """
        :param name:
        :param code:
        :param edate_val:
        :param stock_data:
        :param patlog_obj:
        :param kwargs:
        :return:
        """
        """
        PZ1 := MA(CLOSE, M);
        PZ2 := HHV(HIGH, M);
        PZ3 := LLV(LOW, M);
        PZ4 := (PZ2 - PZ1) / PZ1;
        PZ5 := (PZ1 - PZ3) / PZ1;
        PZ := REF(PZ4, 1) < 0.15 AND REF(PZ5, 1) < 0.15;
        MA10:=MA(C,10);
        MA20:=MA(C,20);
        MA50:=MA(C,50);
        MA120:=MA(C,120);
        MAMAX:=MAX(MAX(MAX(MA10,MA20),MA50),MA120);
        MAMIN:=MIN(MIN(MIN(MA10,MA20),MA50),MA120);
        SL:=MAMAX/MAMIN<1.05;
        ZF := C/REF(C, 1) > 1.05;
        TP1 := HHV(HIGH, M);
        TP := HIGH = TP1;
        PZ AND SL AND ZF AND TP;
        """
        M = kwargs["突破区间窗口"]  # 取周期值
        MEAN_VAR1 = kwargs["第一条均线周期"]
        MEAN_VAR2 = kwargs["第二条均线周期"]
        MEAN_VAR3 = kwargs["第三条均线周期"]
        MEAN_VAR4 = kwargs["第四条均线周期"]
        WAVE_RANGE = kwargs["上下波动幅度"]/100
        MEAN_BOND = kwargs["均线粘合幅度"]/100
        BREAK_PCT = kwargs["突破时涨幅"]/100
        LATEST_CLOSE = np.round(stock_data["收盘价"][-1], 2)

        try:
            PZ1 = stock_data["收盘价"].rolling(window=M).mean() # 计算M日的移动平均线
            PZ2 = stock_data["最高价"].rolling(window=M).max() # 计算M日的最高价
            PZ3 = stock_data["最低价"].rolling(window=M).min() # 计算M日的最低价

            PZ4 = (PZ2 - PZ1) / PZ1 # 计算向上波动幅度
            PZ5 = (PZ1 - PZ3) / PZ1 # 计算向下波动幅度

            PZ = (PZ4.shift(1) < WAVE_RANGE) & (PZ5.shift(1) < WAVE_RANGE) # 选出符合上下波动幅度范围的数据

            MA10 = stock_data["收盘价"].rolling(window=MEAN_VAR1).mean() # 计算10日的移动平均线
            MA20 = stock_data["收盘价"].rolling(window=MEAN_VAR2).mean() # 计算20日的移动平均线
            MA50 = stock_data["收盘价"].rolling(window=MEAN_VAR3).mean() # 计算50日的移动平均线
            MA120 = stock_data["收盘价"].rolling(window=MEAN_VAR4).mean() # 计算120日的移动平均线
            MAMAX = np.maximum(np.maximum(np.maximum(MA10, MA20), MA50), MA120) # 选出各均线中最大值
            MAMIN = np.minimum(np.minimum(np.minimum(MA10, MA20), MA50), MA120) # 选出各均线中最小值
            SL = MAMAX / MAMIN < (1+MEAN_BOND) # 选出符合收敛幅度的数据
            ZF = stock_data["收盘价"]/stock_data["收盘价"].shift(1) > 1+BREAK_PCT # 选出符合涨跌幅的数据
            TP1 = stock_data["最高价"].rolling(window=M).max() # 选出N日日的最高价
            TP = stock_data["最高价"] == TP1 # 选出最高价是N日的最高价的数据

            # print("PZ4")
            # print(PZ4[-5:])
            # print("PZ5")
            # print(PZ5[-5:])
            # print("PZ")
            # print(PZ[-5:])
            # print("SL")
            # print(SL[-5:])
            # print("ZF")
            # print(ZF[-5:])
            # print("TP1")
            # print(TP1[-5:])
            # print("TP")
            # print(TP[-5:])

            if (PZ & SL & ZF & TP)[-1] == True:
                # 输出满足要求的股票
                patlog_obj.re_print("符合特征: 股票 {},代码 {}".format(name, code))
                df_result = pd.DataFrame([[name, code, LATEST_CLOSE]], index=[0], columns=["股票名称", "股票代码", "收盘价"])
                #print(df_result)
                return df_result
            else:
                return pd.DataFrame()
        except Exception as e:
            print(e)
            return pd.DataFrame()

    @staticmethod
    def needle_bottom_raise(name, code, stock_data, patlog_obj, **kwargs):

        """
        :param name:  平安银行
        :param code:  000001.SZ
        :param stock_data:  DataFrame
        :param patlog_obj:
        :param kwargs: dict
        :return:
        """
        """
        DZ := L = LLV(L, 10) AND O/L > 1.05 AND C/L > 1.05;
        PT := BARSSINCEN(DZ, 10); 表示N个周期内满足DZ条件到当前的周期数
        GJ := C > REF(H, PT);
        COUNT(GJ, PT) = 1 AND GJ;
        """
        """
        print(f"股票名称:{name}")
        print(f"股票代码:{code}")
        print(f"股票行情数据:\n{stock_data.tail()}\n{stock_data.describe()}")
        print(f"形态选股参数：\n{kwargs}")
        """
        # 选股算法的参数
        BOTTOM_RATE = 1+kwargs["单针探底的幅度"]/100
        RAISE_RATE = kwargs["探底后回升的幅度"]/100
        OCCUR_RANGE = kwargs["近N日内出现单针信号"]
        VOLUME_RATE = kwargs["单针成交量是近N日内平均成交量的倍数"]

        try:
            LOW_PRICE = stock_data["最低价"] == stock_data["最低价"].rolling(window=OCCUR_RANGE).min()  # 是否是M日的最低价
            DZ = LOW_PRICE & ((stock_data["开盘价"]/stock_data["最低价"])>BOTTOM_RATE) & ((stock_data["收盘价"]/stock_data["最低价"])>BOTTOM_RATE)

            NEEDLE_DF = stock_data[-OCCUR_RANGE:][DZ[-OCCUR_RANGE:]]

            if NEEDLE_DF.empty == True:
                return pd.DataFrame()

            PRICE_ABOVE = stock_data["收盘价"][-1] > NEEDLE_DF["最高价"][0] * (1+RAISE_RATE)
            VOLUME_ABOVE = NEEDLE_DF["成交量"][0] > stock_data["成交量"][-OCCUR_RANGE:].mean() * VOLUME_RATE

            # 如果满足单针探底要求的特征，返回股票代码和名称
            if PRICE_ABOVE & VOLUME_ABOVE:
                # 输出满足要求的股票
                patlog_obj.re_print("符合特征: 股票 {},代码 {}".format(name, code))
                df_result = pd.DataFrame([[name, code]],
                                         index=[0], columns=["股票名称", "股票代码"])
                #print(name, code)
                #print(f"符合特征的股票:\n{df_result}")
                return df_result
            else:
                return pd.DataFrame()

        except Exception as e:
            print(e)
            return pd.DataFrame()

    @staticmethod
    def mult_ma_raise(name, code, stock_data, patlog_obj, **kwargs):

        """
        :param name:  平安银行
        :param code:  000001.SZ
        :param stock_data:  DataFrame
        :param patlog_obj:
        :param kwargs: dict
        :return:
        """
        """
        print(f"股票名称:{name}")
        print(f"股票代码:{code}")
        print(f"股票行情数据:\n{stock_data.tail()}\n{stock_data.describe()}")
        print(f"形态选股参数：\n{kwargs}")
        """
        # 选股算法的参数
        MEAN_VAR1 = kwargs["第一条均线周期"]
        MEAN_VAR2 = kwargs["第二条均线周期"]
        MEAN_VAR3 = kwargs["第三条均线周期"]
        MEAN_VAR4 = kwargs["第四条均线周期"]
        CONTINUE_DAYS = kwargs["连续发散天数"]
        ENLARGE_TIMES = kwargs[u"开口放大倍数"]

        LATEST_CLOSE = np.round(stock_data["收盘价"][-1], 2)

        try:
            MA1 = stock_data["收盘价"].rolling(window=MEAN_VAR1).mean() # 计算M日的移动平均线
            MA2 = stock_data["收盘价"].rolling(window=MEAN_VAR2).mean() # 计算M日的移动平均线
            MA3 = stock_data["收盘价"].rolling(window=MEAN_VAR3).mean() # 计算M日的移动平均线
            MA4 = stock_data["收盘价"].rolling(window=MEAN_VAR4).mean() # 计算M日的移动平均线
            CLOSE = stock_data["收盘价"]
            MA1.fillna(0, inplace=True)
            MA2.fillna(0, inplace=True)
            MA3.fillna(0, inplace=True)
            MA4.fillna(0, inplace=True)

            DIF_MA1_MA4_END = MA1[-1] - MA4[-1]
            DIF_MA1_MA4_START = MA1[-CONTINUE_DAYS] - MA4[-CONTINUE_DAYS]

            recent_stock_data = stock_data[-MEAN_VAR4: -1]
            RAISE_UP_COUNT = len(recent_stock_data[recent_stock_data["涨跌幅"] > 9.97])

            # 循环判断是否连续N日都符合均线多头排列的特征
            for id in range(0, CONTINUE_DAYS+1):

                T = (CLOSE[-1-id] > MA1[-1-id] > MA2[-1-id] > MA3[-1-id] > MA4[-1-id])
                #print(id, T, CLOSE[-1-id], MA1[-1-id], MA2[-1-id], MA3[-1-id], MA4[-1-id])
                if T != True: break # 只要有一天不满足则退出

            # 如果每天都满足均线多头排列则符合特征，返回股票代码和名称
            if (id >= CONTINUE_DAYS) & (DIF_MA1_MA4_END > ENLARGE_TIMES*DIF_MA1_MA4_START):
                # 输出满足要求的股票
                EXPEND_RATIO = np.round(DIF_MA1_MA4_END/DIF_MA1_MA4_START, 2)
                patlog_obj.re_print("符合特征: 股票 {},代码 {}".format(name, code))
                df_result = pd.DataFrame([[name, code, LATEST_CLOSE, EXPEND_RATIO, RAISE_UP_COUNT]],
                                         index=[0], columns=["股票名称", "股票代码", "收盘价", "发散因子(倍)", "近期涨停数"])
                #print(name, code)
                #print(f"符合特征的股票:\n{df_result}")
                return df_result
            else:
                return pd.DataFrame()

        except Exception as e:
            print(e)
            return pd.DataFrame()

    @staticmethod
    def new_high_break(name, code, stock_data, patlog_obj, **kwargs):
        """
        :param name:  平安银行
        :param code:  000001.SZ
        :param stock_data:  DataFrame
        :param patlog_obj:
        :param kwargs: dict
        :return:
        """
        """
        T1 := C/HHV(H,250)>0.95;
        T2 := HHV(H,20) < HHV(H,250);
        T1 AND T2;
    
        print(f"股票名称:{name}")
        print(f"股票代码:{code}")
        print(f"股票行情数据:\n{stock_data.tail()}\n{stock_data.describe()}")
        print(f"形态选股参数：\n{kwargs}")
        """
        # 选股算法的参数
        UNDER_RATE = kwargs["突破高点幅度下限"]/100
        ABOVE_RATE = kwargs["突破高点幅度上限"]/100

        HIGHEST_RANGE = kwargs["突破近N日内高点"]
        TREND_RANGE = kwargs["近期上涨趋势检测天数"]

        try:

            LONG_HIGH_PRICE = stock_data["最高价"][:-TREND_RANGE].rolling(window=HIGHEST_RANGE).max()  # 是否是N日的最高价
            T1 = (stock_data["收盘价"][-1] / LONG_HIGH_PRICE[-1]) > UNDER_RATE
            T2 = (stock_data["收盘价"][-1] / LONG_HIGH_PRICE[-1]) < ABOVE_RATE
            # 判断是否为突破后回落
            DETECT_DROP_AMOUNT = stock_data["最高价"][-TREND_RANGE:] > (LONG_HIGH_PRICE[-1]*ABOVE_RATE)
            # 如果每天都满足均线多头排列则符合特征，返回股票代码和名称
            if T1 & T2 & (len(DETECT_DROP_AMOUNT[DETECT_DROP_AMOUNT == True]) == 0):
                distance_to_high = np.round(stock_data["收盘价"][-1] / LONG_HIGH_PRICE[-1], 2)
                # 输出满足要求的股票
                patlog_obj.re_print("符合特征: 股票 {},代码 {}".format(name, code))
                df_result = pd.DataFrame([[name, code, distance_to_high]],
                                         index=[0], columns=["股票名称", "股票代码", "距离前高比例"])
                #print(name, code)
                #print(f"符合特征的股票:\n{df_result}")
                return df_result
            else:
                return pd.DataFrame()

        except Exception as e:
            print(e)
            return pd.DataFrame()

