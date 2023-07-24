#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    # 用于存储已存在的文件名
    existing_file_names = set()

    # 循环拿到所有存放用例的文件路径
    for i in get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True):
        # 循环读取文件中的数据
        case_process = CaseData(i).case_process(case_id_switch=True)
        if case_process is not None:
            # 转换数据类型
            for case in case_process:
                for k, v in case.items():
                    # 判断 case_id 是否已存在
                    case_id_exit = k in _cache_config.keys()
                    # 如果 case_id 不存在，则将用例写入缓存池中
                    if case_id_exit is False:
                        CacheHandler.update_cache(cache_name=k, value=v)
                        # case_data[k] = v
                    # 当 case_id 存在时，则抛出异常
                    elif case_id_exit is True:
                        INFO.logger.info(f"case_id: {k} 存在重复项, 请修改 case_id, 文件路径: {i}")
                        raise ValueError(f"case_id: {k} 存在重复项, 请修改 case_id, 文件路径: {i}")
                    # 检查文件名是否重复
                    if i in existing_file_names:
                        INFO.logger.info(f"文件名: {i} 存在重复项，请修改文件名")
                        raise ValueError(f"文件名: {i} 存在重复项，请修改文件名")

                    existing_file_names.add(i)

write_case_process()
