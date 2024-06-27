#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
收集 allure 报告
"""

import os
import json
import time
import subprocess
from typing import List, Text
from common.setting import ensure_path_sep
from utils.logging_tool.log_control import logger
from utils.other_tools.models import TestMetrics
from utils.read_files_tools.get_all_files_path import get_all_files


class AllureFileClean:

    """allure 报告数据清洗，提取业务需要得数据"""

    session_start_time = 0
    _cached_case_count = None

    @classmethod
    def get_testcases(cls) -> List:
        """ 获取所有 allure 报告中执行用例的情况"""
        # 将所有数据都收集到files中
        files = []
        for i in get_all_files(ensure_path_sep("\\report\\html\\data\\test-cases")):
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                files.append(date)
        return files

    def get_failed_case(self) -> List:
        """ 获取到所有失败的用例标题和用例代码路径"""
        error_case = []
        for i in self.get_testcases():
            if i['status'] == 'failed' or i['status'] == 'broken':
                error_case.append((i['name'], i['fullName']))
        return error_case

    def get_failed_cases_detail(self) -> Text:
        """ 返回所有失败的测试用例相关内容 """
        date = self.get_failed_case()
        values = ""
        # 判断有失败用例，则返回内容
        if len(date) >= 1:
            values = "失败用例:\n"
            values += "        **********************************\n"
            for i in date:
                values += "        " + i[0] + ":" + i[1] + "\n"
        return values


    @classmethod
    def generate_allure_report(cls) -> None:
        """生成Allure报告"""
        if not cls._cached_case_count:
            project_root = ensure_path_sep(".")
            logger.info("生成最新Allure报告...")
            cmd = "allure generate ./report/tmp -o ./report/html --clean"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_root)
            if result.returncode != 0:
                logger.error(f"生成Allure报告失败: {result.stderr}")
                raise RuntimeError("生成Allure报告失败，请检查Allure环境配置")
            else:
                logger.info("Allure报告生成成功")


    @classmethod
    def set_session_start_time(cls, start_time):
        cls.session_start_time = start_time


    @classmethod
    def get_case_count(cls) -> TestMetrics:
        """ 统计用例数量 return的是字典"""
        if cls._cached_case_count:
            return cls._cached_case_count

        try:
            html_report_path = ensure_path_sep("\\report\\html")
            tmp_report_path = ensure_path_sep("\\report\\tmp")
            summary_file_path = ensure_path_sep("\\report\\html\\widgets\\summary.json")

            if not os.path.exists(html_report_path) or os.path.exists(tmp_report_path):
                cls.generate_allure_report()
            else:
                logger.error("HTML目录已存在，TMP目录不存在，请生成TMP目录...")

            if os.path.exists(summary_file_path):
                with open(summary_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            else:
                logger.error(f"文件 {summary_file_path} 不存在")
                raise FileNotFoundError(f"文件 {summary_file_path} 不存在")

            _case_count = data['statistic']
            _time = data['time']
            keep_keys = {"passed", "failed", "broken", "skipped", "total"}
            run_case_data = {k: v for k, v in _case_count.items() if k in keep_keys}

            # 判断运行用例总数大于0
            if _case_count["total"] > 0:
                # 确保计算通过率时使用浮点数
                passed = _case_count["passed"]
                total = _case_count["total"]
                run_case_data["pass_rate"] = round((passed / total) * 100, 2)
            else:
                # 如果未运行用例，则成功率为 0.0
                run_case_data["pass_rate"] = 0.0
            # 计算 allure_time
            run_case_data['allure_time'] = _time if run_case_data['total'] == 0 else round(_time['duration'] / 1000, 2)

            # 计算 pytest_time 并添加到 run_case_data
            if cls.session_start_time > 0:
                pytest_time = round(time.time() - cls.session_start_time, 2)
                run_case_data['pytest_time'] = pytest_time
            else:
                run_case_data['pytest_time'] = 0
            
            cls._cached_case_count = TestMetrics(**run_case_data)

            return cls._cached_case_count

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "程序中检查到您未生成allure报告，"
                "通常可能导致的原因是allure环境未配置正确，"
                "详情可查看如下博客内容："
                "https://blog.csdn.net/weixin_43865008/article/details/124332793"
            ) from exc

        except Exception as e:
            logger.error(f"处理Allure数据时出错: {e}")
            raise


if __name__ == '__main__':
    allure_data = AllureFileClean.get_case_count(time.time(), time.time())
    print(allure_data)
