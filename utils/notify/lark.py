#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
发送飞书通知
"""
import json
import logging
import time
import datetime
import requests
import urllib3
from utils.other_tools.allure_data.allure_report_data import TestMetrics

from utils import config

# 关闭警告
urllib3.disable_warnings()

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
  非空字符串
  :param content: 字符串
  :return: 非空 - True，空 - False
  """
    return bool(content and content.strip())


class FeiShuTalkChatBot:
    """飞书机器人通知"""

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics

    def send_text(self, msg: str):
        """
        消息类型为text类型
        :param msg: 消息内容
        :return: 返回消息发送结果
        """
        data = {"msg_type": "text", "at": {}}
        if is_not_null_and_blank_str(msg):  # 传入msg非空
            data["content"] = {"text": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        logging.debug('text类型：%s', data)
        return self.post()

    def post(self):
        """
        发送消息（内容UTF-8编码）
        :return: 返回消息发送结果
        """
        at_users = []
        for user_id in config.lark.user_id:
            at_user = {
                "tag": "at",
                "user_id": user_id
            }
            at_users.append(at_user)

        rich_text = {
            "email": "1430066373@qq.com",
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "【自动化测试通知】",
                        "content": [
                            [
                                {
                                    "tag": "a",
                                    "text": "🦊点击查看测试报告",
                                    "href": "http://activate.navicat.com:9999"
                                }
                            ],
                            [
                                *at_users
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "测 试 人 员 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{config.tester_name}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "运 行 环 境 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{config.env}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "总 用 例 数 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.total}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "成功用例数 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.passed}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "失败用例数 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.failed}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "异常用例数 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.broken}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "跳过用例数 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.skipped}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "成   功   率 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.pass_rate} %"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "allure报告测试时长: "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.allure_time}s"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "pytest测试会话时长: "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.pytest_time}s"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "日   期 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{datetime.datetime.now().strftime('%Y-%m-%d')}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "时   间 : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{datetime.datetime.now().strftime('%H:%M:%S')}"
                                }
                            ],
                        ]
                    }
                }
            }
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        post_data = json.dumps(rich_text)
        response = requests.post(
            config.lark.webhook,
            headers=headers,
            data=post_data,
            verify=False
        )
        result = response.json()

        if result.get('StatusCode') != 0:
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            result_msg = result['errmsg'] if result.get('errmsg', False) else '未知异常'
            error_data = {
                "msgtype": "text",
                "text": {
                    "content": f"[注意-自动通知]飞书机器人消息发送失败，时间：{time_now}，"
                               f"原因：{result_msg}，请及时跟进，谢谢!"
                },
                "at": {
                    "isAtAll": False
                }
            }
            logging.error("消息发送失败，自动通知：%s", error_data)
            requests.post(config.lark.webhook, headers=headers, data=json.dumps(error_data))
        return result
