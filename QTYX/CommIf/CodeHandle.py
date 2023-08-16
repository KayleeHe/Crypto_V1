#! /usr/bin/env python
#-*- encoding: utf-8 -*-
#author 元宵大师 本例程仅用于教学目的，严禁转发和用于盈利目的，违者必究

class CodeConvert:

    def conv_ts_code(self, code):
        # 转换为xxxxxx.SZ/xxxxxx.SH格式
        if code.find('.') == 2: # baostock的代码格式
            sym, num = code.upper().split(".")
            ts_code = num + "." + sym
            return ts_code

        elif code.find('.') == -1: # 正常代码格式
            return code + ".SH" if code[0] == '6' else code + ".SZ"  # 行情转tushare格式

        elif code.find('.') == 6:  # tushare的代码格式
            return code
        else:
            return code

    def conv_bs_code(self, code):
        # 转换为sz.xxxxxx/sh.xxxxxx格式
        if code.find('.') == 2: # baostock的代码格式
            return code

        elif code.find('.') == -1: # 正常代码格式
            return "sh." + code if code[0] == '6' else "sz." + code   # 行情转baostock

        elif code.find('.') == 6:  # tushare的代码格式
            num, sym = code.lower().split(".")
            return sym + "." + num
        else:
            return code

    def conv_ts_codes(self, codes)->dict:
        # 自适应转换代码格式成tushare格式
        if isinstance(codes, dict):
            for k, v in codes.items():
                codes[k] = self.conv_ts_code(v)
            return codes
        else:
            return dict()

    def remove_st_codes(self, codes)->dict:

        return dict()