#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from typing import Text


def root_path():
    """ 获取 根路径 """
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def ensure_path_sep(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return root_path() + path


def get_relative_path(target_path, start_path=os.curdir):
    try:
        print(f"Calculating relative path from {start_path} to {target_path}")
        relative_path = os.path.relpath(target_path, start_path)
        print(f"Relative path calculated: {relative_path}")
        return relative_path
    except Exception as e:
        print(f"Error occurred while getting relative path: {e}")
        return None