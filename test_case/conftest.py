#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import time
import allure
import requests
import ast
from common.setting import ensure_path_sep
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


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

    # 记录收集到的测试用例
    collected_items_str = "\n".join([str(item) for item in items])
    logger.info(f"收集到的测试用例:\n{collected_items_str}")

    appoint_items = ["test_login", "test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
                     "test_Clear_Cart_Item"]
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

    # 按指定顺序排序
    sorted_run_items = sorted(run_items, key=lambda x: appoint_items.index(x.name.split("[")[0]))

    # 合并排序后的列表
    items[:] = sorted_run_items + other_items
            

@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    # import json
    # print("原始输入数据:")
    # print(json.dumps(in_data, indent=4, ensure_ascii=False))
    in_data = TestCase(**in_data)
    # 检测is_run条件
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary():
    allure_data = AllureFileClean.get_case_count()

    _PASSED = allure_data.get('passed', 0)
    _BROKEN = allure_data.get('broken', 0)
    _FAILED = allure_data.get('failed', 0)
    _SKIPPED = allure_data.get('skipped', 0)
    _TOTAL = allure_data.get('total', 0)
    allure_time = allure_data.get('time', 0)

    logger.info(f"总用例数: {_TOTAL}")
    logger.info(f"通过用例数: {_PASSED}")
    logger.error(f"异常用例数: {_BROKEN}")
    logger.error(f"失败用例数: {_FAILED}")
    logger.warning(f"跳过用例数: {_SKIPPED}")
    logger.info(f"pytest 用例执行总时长: {allure_time} s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        logger.info(f"用例成功率: {_RATE:.2f} %")
    except ZeroDivisionError:
        logger.info("用例成功率: 0.00 %")
        