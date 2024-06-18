#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import ast
import yaml.scanner
from utils.read_files_tools.regular_control import regular
from common.setting import ensure_path_sep


class GetYamlData:
    """ 获取 yaml 文件中的数据 """

    def __init__(self, file_dir):
        self.file_dir = str(file_dir)

    def get_yaml_data(self) -> dict:
        if os.path.exists(self.file_dir):
            with open(self.file_dir, 'r', encoding='utf-8') as f:
                _data = yaml.safe_load(f)  # yaml.load是不安全的
                return _data
        else:
            raise FileNotFoundError(f"文件路径不存在")


    def write_yaml_data(self, key: str, value) -> int:
        """
        更改 yaml 文件中的值, 并且保留注释内容
        :param key: 字典的key
        :param value: 写入的值
        :return:
        """
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            # 创建了一个空列表，里面没有元素
            lines = []
            for line in file.readlines():
                if line != '\n':
                    lines.append(line)
            file.close()

        with open(self.file_dir, 'w', encoding='utf-8') as file:
            flag = 0
            for line in lines:
                left_str = line.split(":")[0]
                if key == left_str.lstrip() and '#' not in line:
                    newline = f"{left_str}: {value}"
                    line = newline
                    file.write(f'{line}\n')
                    flag = 1
                else:
                    file.write(f'{line}')
            file.close()
            return flag


class GetCaseData(GetYamlData):
    """ 获取测试用例中的数据 """

    def get_different_formats_yaml_data(self) -> list:
        """
        获取兼容不同格式的yaml数据
        :return:
        """
        res_list = []
        for i in self.get_yaml_data():
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """
        获取测试用例数据, 转换成指定数据格式
        :return:
        """

        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = regular(str(_yaml_data))
        return ast.literal_eval(re_data)
if __name__ == '__main__':
    ym = GetYamlData(ensure_path_sep("\\util"))
    ym.get_yaml_data()