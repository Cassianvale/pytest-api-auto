#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""日志封装"""

from loguru import logger
import time
from pathlib import Path
from common.setting import ensure_path_sep

# 创建日志文件目录
now_time_day = time.strftime("%Y-%m-%d", time.localtime())
logs_dir = Path(ensure_path_sep("\\logs"))
logs_dir.mkdir(parents=True, exist_ok=True)


# info记录所有等级的日志，error记录error等级的日志，warning记录warning等级的日志
logger.add(
    ensure_path_sep(f"\\logs\\info-{now_time_day}.log"),
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} {level} {module} py:{line} {message}",
    rotation="1 day",
    retention="3 days",
    encoding="utf-8"
)

logger.add(
    ensure_path_sep(f"\\logs\\error-{now_time_day}.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} {level} {module} py:{line} {message}",
    rotation="1 day",
    retention="3 days",
    encoding="utf-8"
)

logger.add(
    ensure_path_sep(f"\\logs\\warning-{now_time_day}.log"),
    level="WARNING",
    format="{time:YYYY-MM-DD HH:mm:ss} {level} {module} py:{line} {message}",
    rotation="1 day",
    retention="3 days",
    encoding="utf-8"
)


if __name__ == '__main__':
    try:
        logger.info("这是一条信息日志")
        logger.critical("这是一条严重日志")
        logger.warning("这是一条警告日志")
        
        # 模拟异常以记录堆栈跟踪信息
        1 / 0
    except Exception as e:
        logger.exception("发生了异常")