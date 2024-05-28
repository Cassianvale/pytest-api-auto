#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os, shutil
from common.setting import ensure_path_sep
from utils.logging_tool.log_control import INFO

'''
清空test_case目录下所有已经生成的用例
'''

def del_directories(path):
    """清空目录下的所有文件夹，排除__init__.py和conftest.py文件"""
    if not os.path.isdir(path):
        INFO.logger.error(f"路径不存在: {path}")
        return

    INFO.logger.info(f"开始清空目录: {path}")

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not (dir == "venv"):
                shutil.rmtree(dir_path)
                INFO.logger.info(f"已删除文件夹: {dir_path}")

        # 保留__init__和conftest
        for file in files:
            file_path = os.path.join(root, file)
            if not (file == "__init__.py" or file == "conftest.py"):
                os.remove(file_path)
                INFO.logger.info(f"已删除文件: {file_path}")

    INFO.logger.info(f"目录清空完成: {path}")
