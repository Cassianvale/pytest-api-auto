#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import traceback
import pytest

from common.setting import ensure_path_sep
from utils import config
from utils.read_files_tools.case_automatic_control import TestCaseAutomaticGeneration
from utils.other_tools.models import NotificationType
from utils.logging_tool.log_control import logger
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics
from utils.logging_tool.log_control import logger
from utils.read_files_tools.clean_case import del_directories


def run():

    # 从配置文件中获取项目名称
    try:
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

        # 判断现有的测试用例，如果未生成测试代码，则自动生成
        # 不能存在相同case_id和相同文件名的用例，否则报错并exit
        TestCaseAutomaticGeneration().get_case_automatic()

        """正常运行"""
        pytest.main([
            '-s',  # 实时输出
            '-W', 'ignore:Module already imported:pytest.PytestWarning',  # 忽略特定警告
            '--alluredir', './report/tmp',  # 指定Allure报告目录
            '--clean-alluredir'  # 清理Allure报告目录
        ])

        """xdist分布式运行"""
        # pytest.main([
        #     '-s',  # 实时输出
        #     '-W', 'ignore:Module already imported:pytest.PytestWarning',  # 忽略特定警告
        #     '--alluredir', './report/tmp',  # 指定Allure报告目录
        #     '--clean-alluredir',  # 清理Allure报告目录
        #     '-n', 'auto',  # 使用pytest-xdist进行并行运行
        #     '--dist', 'loadscope',  # 按测试模块（或类）顺序执行
        # ])

        # 检查临时结果文件是否生成
        if os.path.exists('./report/tmp'):
            print("Allure temporary results generated successfully")
        else:
            print("Failed to generate Allure temporary results")

        """
                   --reruns: 失败重跑次数
                   --count: 重复执行次数
                   -v: 显示错误位置以及错误的详细信息
                   -s: 等价于 pytest --capture=no 可以捕获print函数的输出
                   -q: 简化输出信息
                   -m: 运行指定标签的测试用例
                   -x: 一旦错误，则停止运行
                   --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
                    "--reruns=3", "--reruns-delay=2"
        """

        os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        allure_data_dict = AllureFileClean().get_case_count()

        # 将字典转换为TestMetrics实例
        allure_data = TestMetrics(**allure_data_dict)
        excel_path = ensure_path_sep("\\Files\\test_data\\自动化异常测试用例.xlsx")

        notification_mapping = {
            NotificationType.FEI_SHU.value[0]: FeiShuTalkChatBot(allure_data).post,
            NotificationType.DING_TALK.value[0]: DingTalkSendMsg(allure_data).send_ding_notification,
            NotificationType.WECHAT.value[0]: WeChatSend(allure_data).send_wechat_notification,
            NotificationType.EMAIL.value[0]: lambda: SendEmail(allure_data).send_main(attachment_path=excel_path)
        }

        if config.notification_type != NotificationType.DEFAULT.value[0]:
            # 从配置中获取通知类型列表
            notify_type = config.notification_type.split(",")
            # 获取通知类型名称
            notification_names = [
                enum_member.value[1] for enum_member in NotificationType
                if any(enum_member.value[0] == n_type.strip() for n_type in config.notification_type.split(","))
            ]
            # 如果有通知类型，就执行相应的方法
            for n_type in notify_type:
                # 确保 n_type.strip() 是 notification_mapping 的一个键
                if n_type.strip() in notification_mapping:
                    notification_mapping[n_type.strip()]()
                else:
                    print(f"未知的notification类型: {n_type.strip()}")

            # 输出发送通知的类型
            print("==============================================")
            print(f"已发送通知到: {', '.join(notification_names)}")
            print("==============================================")

            # 收集运行失败的用例，整理成excel报告(ErrorCaseExcel自定义excel样式)
            if config.excel_report:
                ErrorCaseExcel().write_case()

            # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
            os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")

    except Exception:
        # 异常邮件发送
        err = traceback.format_exc()
        send_email = SendEmail(AllureFileClean.get_case_count())
        send_email.error_mail(err)
        raise


if __name__ == '__main__':
    try:
        """清空已自动生成的用例重新运行(无需要注释下面两行即可)"""
        # directory = ensure_path_sep("\\test_case")
        # del_directories(directory)
        run()
    except Exception as e:
        logger.exception("An exception occurred")

