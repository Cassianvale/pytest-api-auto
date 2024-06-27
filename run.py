#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import pytest
from common.setting import ensure_path_sep
from test_case.conftest import handle_allure_cache
from utils import config
from utils.logging_tool.log_control import logger
from utils.read_files_tools.clean_case import del_directories
from utils.read_files_tools.case_automatic_control import TestCaseAutomaticGeneration
from utils.other_tools.models import NotificationType
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from utils.other_tools.allure_data.allure_report_data import AllureFileClean


def initialize_logger():
    logger.info(
        """
                         _    _         _      _____         _
          __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
         / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
        | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
         \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
              |_|
              开始执行{}项目...
            """.format(config.project_name)
    )


def generate_test_cases():
    TestCaseAutomaticGeneration().get_case_automatic()


def run_pytest():
    pytest_args = [
        '-s',
        '-W', 'ignore:Module already imported:pytest.PytestWarning',
        '--cache-clear',
        '--alluredir', './report/tmp',
        '--clean-alluredir'
    ]

    if config.use_xdist:
        logger.info("正在使用 pytest-xdist 进行分布式测试...")
        pytest_args.extend([
            '-n', '4',
            '--dist', 'loadscope'
        ])

    pytest.main(pytest_args)


def send_notifications(allure_data):
    notification_mapping = {
        NotificationType.FEI_SHU.value[0]: FeiShuTalkChatBot(allure_data).post,
        NotificationType.DING_TALK.value[0]: DingTalkSendMsg(allure_data).send_ding_notification,
        NotificationType.WECHAT.value[0]: WeChatSend(allure_data).send_wechat_notification,
        NotificationType.EMAIL.value[0]: lambda: SendEmail(allure_data).send_main(
            attachment_path=ensure_path_sep("\\Files\\test_data\\自动化异常测试用例.xlsx"))
    }

    if config.notification_type != NotificationType.DEFAULT.value[0]:
        notify_type = config.notification_type.split(",")
        for n_type in notify_type:
            if n_type.strip() in notification_mapping:
                notification_mapping[n_type.strip()]()
            else:
                logger.error(f"未知的通知类型: {n_type.strip()}")
        notification_names = [
            enum_member.value[1] for enum_member in NotificationType
            if any(enum_member.value[0] == n_type.strip() for n_type in config.notification_type.split(","))
        ]
        logger.info(f"已发送通知到: {', '.join(notification_names)}")


def write_error_case_excel():
    if config.excel_report:
        ErrorCaseExcel().write_case()


def serve_allure_report():
    os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")


def handle_exception(e):
    err = traceback.format_exc()
    send_email = SendEmail(AllureFileClean().get_case_count())
    send_email.error_mail(err)
    raise e


def clear_test_case():
    directory = ensure_path_sep("\\test_case")
    del_directories(directory)


def run():
    try:
        initialize_logger()
        clear_test_case()  # 运行前清空已生成的测试用例
        generate_test_cases()  # 自动生成测试用例
        run_pytest()
        allure_data = handle_allure_cache("allure_data_cache")  # 处理 allure 数据缓存
        send_notifications(allure_data)  # 发送通知
        write_error_case_excel()  # 写入异常用例excel
        # serve_allure_report()   # 自动打开 Allure 报告
    except Exception as e:
        handle_exception(e)


if __name__ == '__main__':
    run()
