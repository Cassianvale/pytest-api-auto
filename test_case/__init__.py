#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from common.setting import ensure_path_sep, get_relative_path, root_path
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.cache_process.cache_control import CacheHandler, _cache_config
from utils.logging_tool.log_control import logger


def check_duplicate(file_map, key, current_path):
    if key in file_map:
        existing_path = file_map[key]
        existing_relative_path = get_relative_path(existing_path, root_path())
        raise ValueError(f"{key} 重复，路径分别为：{current_path} 和 {existing_relative_path}")
    file_map[key] = current_path


def write_case_process():
    """
    获取所有用例，写入用例池中
    :return:
    """

    file_name_map = {}
    case_id_map = {}

    for file_path in get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True):
        relative_path = get_relative_path(file_path, root_path())
        file_name = os.path.basename(file_path)

        check_duplicate(file_name_map, file_name, relative_path)

        case_process = CaseData(file_path).case_process(case_id_switch=True)
        if case_process:
            for case in case_process:
                for case_id, value in case.items():
                    check_duplicate(case_id_map, case_id, relative_path)
                    CacheHandler.update_cache(cache_name=case_id, value=value)


try:
    write_case_process()
except ValueError as e:
    logger.error(f"ValueError occurred: {e}")
    sys.exit(1)
