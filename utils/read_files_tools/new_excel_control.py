#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''pandas重写excel控制器'''

import json
import pandas as pd
from common.setting import ensure_path_sep
from utils.logging_tool.log_control import INFO, ERROR
from typing import Union

excel_path = ensure_path_sep("\\Files\\test_data\\test.xlsx")


def get_excel_data(sheet: str, case_name: Union[str, int], request_data_row: int, response_data_row: int):
    """获取excel测试用例数据"""

    res_list = []
    try:
        # 如果输入的sheet值不存在

        df = pd.read_excel(excel_path, sheet_name=sheet)
        # 获取第一列（索引为1）的所有值，除了表头
        column_values = df.iloc[0:, 1].tolist()

        for row_index, value in enumerate(column_values):
            if isinstance(value, int):
                case_name = int(case_name)
            else:
                case_name = str(case_name)
            # 如果找到完全匹配的case_name
            if value == case_name:
                # 获取case_name所在行对应num1和num2列的值
                num1, num2 = df.iloc[row_index, request_data_row], df.iloc[row_index, response_data_row]

                num1 = "Null" if pd.isna(num1) else num1
                num2 = "Null" if pd.isna(num2) else num2

                res_list.append((num1, json.loads(num2)))

        if not res_list:
            # 如果没有找到完全匹配的case_name，进行模糊查询
            fuzzy_matches = [value for value in column_values if case_name in str(value)]

            if fuzzy_matches:
                print(f"未找到与 `{case_name}` 完全匹配的用例名称，是否您要找的是以下这些？")
                for i, match in enumerate(fuzzy_matches):
                    print(f"{i + 1}.  {match}")
                answer = input("如果是的话请输入对应的序号：")
                if answer.isdigit() and 1 <= int(answer) <= len(fuzzy_matches):
                    # 如果用户确认，再次调用函数进行查询
                    return get_excel_data(sheet, fuzzy_matches[int(answer) - 1], request_data_row, response_data_row)
            else:
                ERROR.logger.error(f"未找到与 `{case_name}` 匹配的用例名称！")
                return None
        else:
            INFO.logger.info(
                "获取 {0} 表 \n "
                "📝 Case name: {1} \n "
                "🚀 Request body: {2} \n "
                "🌟 Response: {3} \n "
                "============================================================================"
                .format(sheet, case_name, res_list[0][0], res_list[0][1]))
            return res_list

    except ValueError as e:
        ERROR.logger.error(f"出现错误：{str(e)}, 请检查 `sheet` 参数值是否存在！")
        return None


def set_excel_data(sheet_name: str):
    """从一个 Excel 文件中读取数据，并返回一个 DataFrame 对象"""
    try:
        # 读取 Excel 文件
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(df)
        return df
    except FileNotFoundError as e:
        print(f"文件未找到：{str(e)}")
        return None
    except KeyError as e:
        print(f"工作表未找到：{str(e)}")
        return None


if __name__ == '__main__':
    get_excel_data("Sheet1", 7, 6, 11)
    set_excel_data('Sheet1')
