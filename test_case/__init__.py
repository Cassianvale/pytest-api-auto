#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from common.setting import ensure_path_sep
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.cache_process.cache_control import CacheHandler, _cache_config
from utils.logging_tool.log_control import INFO,WARNING,ERROR

def write_case_process():
    """
    获取所有用例，写入用例池中
    :return:
    """

    # 存储已经存在的文件名
    file_names = set()

    # 循环拿到所有存放用例的文件路径
    for i in get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True):
        # 获取文件名
        file_name = os.path.basename(i)

        # 检查文件名是否重复
        if file_name in file_names:
            INFO.logger.info(f" {i} 存在重复文件名，请修改文件名: {file_name}")
            raise ValueError(f" {i} 存在重复文件名，请修改文件名: {file_name}")
        # 将文件名添加到已存在的文件名集合中
        file_names.add(file_name)

        # 循环读取文件中的数据
        case_process = CaseData(i).case_process(case_id_switch=True)
        if case_process is not None:
            # 转换数据类型
            for case in case_process:
                for k, v in case.items():
                    # 判断 case_id 是否已存在
                    case_id_exit = k in _cache_config.keys()
                    # 如果case_id 不存在，则将用例写入缓存池中
                    if case_id_exit is False:
                        CacheHandler.update_cache(cache_name=k, value=v)
                        # case_data[k] = v
                    # 当 case_id 为 True 存在时，则抛出异常
                    elif case_id_exit is True:
                        INFO.logger.info(f"{i} 存在重复case_id, 请修改case_id名称: {k}")
                        raise ValueError(f"{i} 存在重复case_id, 请修改case_id名称: {k}")

write_case_process()