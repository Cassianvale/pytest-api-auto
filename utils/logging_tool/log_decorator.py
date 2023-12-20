#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
日志装饰器，控制程序日志输入，默认为 True
如设置 False，则程序不会打印日志
"""
import ast
from functools import wraps
from utils.read_files_tools.regular_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR


def log_decorator(switch: bool):
    """
    封装日志装饰器, 打印请求信息
    :param switch: 定义日志开关
    :return:
    """
    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs):

            # 判断日志为开启状态，才打印日志
            res = func(*args, **kwargs)
            # 判断日志开关为开启状态
            if switch:
                _log_msg = f"\n======================================================\n"\
                    f"🦊 <Title>: {res.detail}\n" \
                    f"🚀 <Request>:  \n" \
                    f"      URL: {res.url}\n" \
                    f"      Request method: {res.method}\n" \
                    f"      Request headers: {res.headers}\n" \
                    f"      Request body: {res.request_body}\n" \
                    f"🌟 <Response>: {res.response_data}\n" \
                    f"⏰ <Response time>: {res.res_time}\n (ms)" \
                    f"🧩 <Response code>: {res.status_code}\n" \
                    "====================================================="
                _is_run = ast.literal_eval(cache_regular(str(res.is_run)))
                # 判断正常打印的日志，控制台输出绿色
                if _is_run in (True, None) and res.status_code == 200:
                    INFO.logger.info(_log_msg)
                else:
                    # 失败的用例，控制台打印红色
                    ERROR.logger.error(_log_msg)
            return res
        return swapper
    return decorator
