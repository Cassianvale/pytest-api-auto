#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.setting import ensure_path_sep
from utils.read_files_tools.clean_case import del_directories
from run import run

"""清空已自动生成的用例，重新运行"""

if __name__ == '__main__':
    directory = ensure_path_sep("\\test_case")
    del_directories(directory)
    run()
