#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 13:22
# @Author : 余少琪
"""
import os
from typing import Text, Dict
from common.setting import ensure_path_sep
from utils.read_files_tools.testcase_template import write_testcase_file
from utils.read_files_tools.yaml_control import GetYamlData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.other_tools.exceptions import ValueNotFoundError


class TestCaseAutomaticGeneration:

    def __init__(self):
        self.yaml_case_data = None
        self.file_path = None

    @property
    def case_date_path(self) -> Text:
        """返回 yaml 用例文件路径"""
        return ensure_path_sep("\\data")

    @property
    def case_path(self) -> Text:
        """ 存放用例代码路径"""
        return ensure_path_sep("\\test_case")

    @property
    def allure_epic(self):
        _allure_epic = self.yaml_case_data.get("case_common").get("allureEpic")
        assert _allure_epic is not None, (
                "用例中 allureEpic 为必填项，请检查用例内容, 用例路径：'%s'" % self.file_path
        )
        return _allure_epic

    @property
    def allure_feature(self):
        _allure_feature = self.yaml_case_data.get("case_common").get("allureFeature")
        assert _allure_feature is not None, (
                "用例中 allureFeature 为必填项，请检查用例内容, 用例路径：'%s'" % self.file_path
        )
        return _allure_feature

    @property
    def allure_story(self):
        _allure_story = self.yaml_case_data.get("case_common").get("allureStory")
        assert _allure_story is not None, (
                "用例中 allureStory 为必填项，请检查用例内容, 用例路径：'%s'" % self.file_path
        )
        return _allure_story

    @property
    def file_name(self) -> Text:
        """
        通过 yaml文件的命名，将名称转换成 py文件的名称
        :return:  示例： DateDemo.py
        """
        i = len(self.case_date_path)
        yaml_path = self.file_path[i:]
        file_name = None
        # 路径转换
        if '.yaml' in yaml_path:
            file_name = yaml_path.replace('.yaml', '.py')
        elif '.yml' in yaml_path:
            file_name = yaml_path.replace('.yml', '.py')
        return file_name

    @property
    def get_test_class_title(self):
        """
        自动生成类名称
        :return: sup_apply_list --> SupApplyList
        """
        # 提取文件名称
        _file_name = os.path.split(self.file_name)[1][:-3]
        _name = _file_name.split("_")
        _name_len = len(_name)
        # 将文件名称格式，转换成类名称: sup_apply_list --> SupApplyList
        for i in range(_name_len):
            _name[i] = _name[i].capitalize()
        _class_name = "".join(_name)

        return _class_name

    @property
    def func_title(self) -> Text:
        """
        函数名称
        :return:
        """
        return os.path.split(self.file_name)[1][:-3]

    @property
    def spilt_path(self):
        path = self.file_name.split(os.sep)
        path[-1] = path[-1].replace(path[-1], "test_" + path[-1])
        return path

    @property
    def get_case_path(self):
        """
        根据 yaml 中的用例，生成对应 testCase 层代码的路径
        :return: D:\\Project\\test_case\\test_case_demo.py
        """
        new_name = os.sep.join(self.spilt_path)
        return ensure_path_sep("\\test_case" + new_name)

    @property
    def case_ids(self):
        return [k for k in self.yaml_case_data.keys() if k != "case_common"]

    @property
    def get_file_name(self):
        # 这里通过“\\” 符号进行分割，提取出来文件名称
        # 判断生成的 testcase 文件名称，需要以test_ 开头
        case_name = self.spilt_path[-1].replace(
            self.spilt_path[-1], "test_" + self.spilt_path[-1]
        )
        return case_name

    def mk_dir(self) -> None:
        """ 判断生成自动化代码的文件夹路径是否存在，如果不存在，则自动创建 """
        # _LibDirPath = os.path.split(self.libPagePath(filePath))[0]

        _case_dir_path = os.path.split(self.get_case_path)[0]
        if not os.path.exists(_case_dir_path):
            os.makedirs(_case_dir_path)

    def get_case_automatic(self) -> None:
        """ 自动生成 测试代码"""
        file_path = get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True)

        for file in file_path:
            # 判断代理拦截的yaml文件，不生成test_case代码
            if 'proxy_data.yaml' not in file:
                # 判断用例需要用的文件夹路径是否存在，不存在则创建
                self.yaml_case_data = GetYamlData(file).get_yaml_data()
                self.file_path = file
                self.mk_dir()
                write_testcase_file(
                    allure_epic=self.allure_epic,
                    allure_feature=self.allure_feature,
                    class_title=self.get_test_class_title,
                    func_title=self.func_title,
                    case_path=self.get_case_path,
                    case_ids=self.case_ids,
                    file_name=self.get_file_name,
                    allure_story=self.allure_story
                    )


if __name__ == '__main__':
    TestCaseAutomaticGeneration().get_case_automatic()
