import unittest
from unittest.mock import patch
import pytest
import time
import allure
import requests
import ast
from common.setting import ensure_path_sep
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.cache_process.cache_control import CacheHandler


class TestClassUser(unittest.TestCase):
    def setUp(self):
        self.your_object = testuser()

    @patch('requests.post')  # 使用patch装饰器模拟requests.post方法
    def test_work_login_init(self, mock_post):
        # 模拟请求返回的JSON数据
        mock_post.return_value.json.return_value = {
            'detail': '此令牌对任何类型的令牌无效',
            'code': 'token_not_valid',
            'messages': [
                {
                    'token_class': 'AccessToken',
                    'token_type': 'access',
                    'message': '令牌无效或已过期'
                }
            ]
        }

        # 使用assertRaises验证函数是否引发了预期的异常
        with self.assertRaises(Exception):
            self.your_object.work_login_init()

        # 验证请求是否正确调用
        mock_post.assert_called_once_with(
            url='http://127.0.0.1:8000/api/users/login',
            json={
                'username': 'admin',
                'password': 123456
            },
            verify=True,
            headers={'Content-Type': 'application/json'}
        )


if __name__ == '__main__':
    unittest.main()
