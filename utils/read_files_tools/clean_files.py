#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清除文件
"""

import os


def del_file(path):
    """删除目录下的文件"""
    if not os.path.isdir(path):
        return

    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)