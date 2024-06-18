#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel控制器
"""

import json
import xlrd
from xlutils.copy import copy
from common.setting import ensure_path_sep


def get_excel_data(sheet_name: str, case_name: any) -> list:
    res_list = []

    excel_dire = ensure_path_sep("\\Files\\TestLogin.xlsx")
    work_book = xlrd.open_workbook(excel_dire)

    # 打开对应的子表
    work_sheet = work_book.sheet_by_name(sheet_name)
    # 读取一行
    idx = 0
    # 遍历第二列除了表头的所有行，并提取

    for one in work_sheet.col_values(1):
        print(one)  # 可能包含浮点数导致无法迭代
        if isinstance(one, str):
            # 运行需要运行的测试用例
            if case_name in one:
                # 从该行提取请求体、响应数据
                req_body_data = work_sheet.cell(idx, 9).value
                resp_data = work_sheet.cell(idx, 11).value
                if resp_data:
                    try:
                        res_list.append((req_body_data, json.loads(resp_data)))
                    except json.decoder.JSONDecodeError:
                        print("Invalid JSON data:", resp_data)
                idx += 1
    print(res_list)
    return res_list


def set_excel_data(sheet_index: int) -> tuple:
    """
    excel 写入
    :return:
    """
    excel_dire = '../Files/TestLogin.xlsx'
    work_book = xlrd.open_workbook(excel_dire, formatting_info=True)
    work_book_new = copy(work_book)

    work_sheet_new = work_book_new.get_sheet(sheet_index)
    return work_book_new, work_sheet_new


if __name__ == '__main__':
    get_excel_data("Sheet1", "44")
