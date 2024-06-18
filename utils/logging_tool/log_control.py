#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""日志封装，可设置不同等级的日志颜色"""

import logging
from logging import handlers
from typing import Text
import colorlog
import time
from pathlib import Path
from common.setting import ensure_path_sep


class LogHandler:
    """ 日志打印封装 """
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    level_symbols = {
        'info': "✅",
        'warning': "⚠️",
        'error': "❌",
        'debug': "🐞",
        'critical': "❗"
    }

    def __init__(self, filename: str, level: str = 'info', when: str = 'D', backup_count: int = 3):
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations[level])

        # 设置屏幕输出和文件输出的格式
        formatter_screen = self.create_color_formatter()
        formatter_file = logging.Formatter(
            fmt="%(symbol)s %(levelname)-8s%(asctime)s %(module)s py:%(lineno)d %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 屏幕输出设置
        screen_handler = logging.StreamHandler()
        screen_handler.setFormatter(formatter_screen)
        self.logger.addHandler(screen_handler)

        # 文件输出设置
        file_handler = handlers.TimedRotatingFileHandler(
            filename=filename, when=when, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setFormatter(formatter_file)
        self.logger.addHandler(file_handler)

        # 添加自定义过滤器以在日志消息前添加符号
        self.logger.addFilter(self.SymbolFilter(self.level_symbols, level))

    class SymbolFilter(logging.Filter):
        """ 用于在日志消息前添加符号的过滤器 """
        def __init__(self, symbols, level):
            super().__init__()
            self.symbols = symbols
            self.level = level

        def filter(self, record):
            record.symbol = self.symbols.get(record.levelname.lower(), "")
            return True

    @staticmethod
    def create_color_formatter():
        """ 设置带颜色的日志格式 """
        colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
        return colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(module)s] [%(lineno)d] [%(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors=colors
        )

    def log_exception(self, msg, *args, **kwargs):
        """ 记录异常信息，确保堆栈跟踪信息被记录 """
        self.logger.error(msg, exc_info=True, *args, **kwargs)


# 创建日志文件目录
now_time_day = time.strftime("%Y-%m-%d", time.localtime())
logs_dir = Path(ensure_path_sep("\\logs"))
logs_dir.mkdir(parents=True, exist_ok=True)

# 创建不同级别的日志处理器
INFO = LogHandler(ensure_path_sep(f"\\logs\\info-{now_time_day}.log"), level='info')
ERROR = LogHandler(ensure_path_sep(f"\\logs\\error-{now_time_day}.log"), level='error')
# DEBUG = LogHandler(ensure_path_sep(f"\\logs\\debug-{now_time_day}.log"), level='debug')
WARNING = LogHandler(ensure_path_sep(f"\\logs\\warning-{now_time_day}.log"), level='warning')

if __name__ == '__main__':
    try:
        INFO.logger.info("This is an info message")
        INFO.logger.error("This is an error message")
        INFO.logger.critical("This is a critical message")
        # DEBUG.logger.info("Debug Info message")
        # DEBUG.logger.debug("Debug message")
        ERROR.logger.error("This is an error message")
        WARNING.logger.warning("This is a warning message")

        # 模拟异常以记录堆栈跟踪信息
        1 / 0
    except Exception as e:
        ERROR.log_exception("An exception occurred")
