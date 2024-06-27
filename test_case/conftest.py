#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import pytest
import allure
import requests
import time
from datetime import datetime
from utils.cache_process.cache_control import Cache
from common.setting import ensure_path_sep
from utils.other_tools.models import TestMetrics
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import logger
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.cache_process.cache_control import CacheHandler
from utils.other_tools.allure_data.allure_report_data import AllureFileClean


def send_verify_code(phone):
    """发送验证码"""
    response = requests.get(url=f"https://www.wanandroid.com/user/register/captcha/sent/{phone}",
                            params={"phone": phone}).json()
    if response['code'] == 0 or response['msg'] == 'success':
        return response
    else:
        raise Exception(f'发送验证码失败: {response}')


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    获取登录的cookie
    :return:
    """

    url = "https://www.wanandroid.com/user/login"
    data = {
        "username": 18800000001,
        "password": 123456
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # 请求登录接口

    res = requests.post(url=url, data=data, verify=True, headers=headers)
    response_cookie = res.cookies

    cookies = ''
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    del_file(ensure_path_sep("\\report"))


def pytest_configure(config):
    config.addinivalue_line("markers", 'smoke')
    config.addinivalue_line("markers", '回归测试')


def pytest_configure(config):
    if not hasattr(config, 'workerinput'):
        # This is the main process
        config.is_master = True
    else:
        # This is a worker process
        config.is_master = False


def pytest_collection_modifyitems(config, items):
    if config.is_master:

        # 对item进行编码处理，确保中文字符正常显示
        for item in items:
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

        appoint_items = ["test_login", "test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD",
                            "test_Guest_ADD","test_Clear_Cart_Item"]
        
        appoint_set = set(appoint_items)  # 使用集合加快查找速度

        # 将items列表拆分成指定顺序项目及其他未指定顺序项目
        run_items = []
        other_items = []
        for item in items:
            module_item = item.name.split("[")[0]
            if module_item in appoint_set:
                run_items.append(item)
            else:
                other_items.append(item)

        sorted_run_items = sorted(run_items, key=lambda x: appoint_items.index(x.name.split("[")[0]))

        items[:] = sorted_run_items + other_items

        collected_items_str = "\n".join([str(item) for item in items])
        logger.info(f"收集到的测试用例:\n{collected_items_str}")


def handle_allure_cache(filename):
    """
    处理 Allure 数据缓存
    :param filename: 缓存文件名
    :return: Allure 数据
    """
    cache = Cache(filename)
    cached_data = cache.get_cache()

    if cached_data:
        try:
            # 取出字典中的实际数据
            allure_data_content = cached_data.get("allure_data")
            if allure_data_content is not None:
                # 将数据传递给 TestMetrics 初始化方法
                allure_data = TestMetrics(**allure_data_content)
                logger.info("从缓存中读取 allure 数据成功")
            else:
                raise KeyError("缓存中未找到关键键 'allure_data'")
        except (TypeError, KeyError) as e:
            logger.error(f"从缓存中读取 allure 数据失败: {e}")
            allure_data = AllureFileClean.get_case_count()
            cache.set_cache("allure_data", allure_data.__dict__)
            logger.info("Allure 数据缓存成功")
    else:
        logger.error("缓存文件不存在或读取失败，重新获取 allure 数据")
        allure_data = AllureFileClean.get_case_count()
        cache.set_cache("allure_data", allure_data.__dict__)
        logger.info("Allure 数据缓存成功")

    return allure_data

def save_allure_cache(filename, allure_data):
    cache = Cache(filename)
    cache.set_cache("allure_data", allure_data.__dict__)
    

@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    # import json
    # print("原始输入数据:")
    # print(json.dumps(in_data, indent=4, ensure_ascii=False))
    in_data = TestCase(**in_data)
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if config.is_master:

        session_start_time = terminalreporter._sessionstarttime

        AllureFileClean.set_session_start_time(session_start_time)

        # 获取 case count
        allure_data = AllureFileClean.get_case_count()
        
        # 缓存 allure_data
        save_allure_cache("allure_data_cache", allure_data)

        _PASSED = allure_data.passed
        _BROKEN = allure_data.broken
        _FAILED = allure_data.failed
        _SKIPPED = allure_data.skipped
        _TOTAL = allure_data.total
        allure_time = allure_data.allure_time
        pytest_time = round(time.time() - session_start_time, 2)
        
        logger.info(f"总用例数: {_TOTAL}")
        logger.info(f"通过用例数: {_PASSED}")
        logger.error(f"异常用例数: {_BROKEN}")
        logger.error(f"失败用例数: {_FAILED}")
        logger.warning(f"跳过用例数: {_SKIPPED}")

        try:
            _RATE = _PASSED / _TOTAL * 100
            logger.info(f"用例成功率: {_RATE:.2f} %")
        except ZeroDivisionError:
            logger.info("用例成功率: 0.00 %")
            
        logger.info(f"allure 报告测试时长: {allure_time} s")

        logger.info(f"pytest 测试会话时长: {pytest_time} s")


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_case\\conftest.py'])
