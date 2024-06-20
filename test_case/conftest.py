#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import time
import allure
import requests
import ast
from common.setting import ensure_path_sep
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
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
    config.addinivalue_line("markers", "dependency: mark test to be dependent on other tests")


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    """
    dependencies = {}
    standalone_items = []

    for item in items:
        # 解码 item 的 name 和 nodeid
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

        dependency_marker = item.get_closest_marker("dependency")
        if dependency_marker:
            depends = dependency_marker.kwargs.get("depends")
            if depends:
                for dep in depends:
                    if dep not in dependencies:
                        dependencies[dep] = []
                    dependencies[dep].append(item)
            else:
                if item.nodeid not in dependencies:
                    dependencies[item.nodeid] = []
        else:
            standalone_items.append(item)

    sorted_items = []
    for dep, dep_items in dependencies.items():
        if dep not in [i.nodeid for i in items]:
            continue
        dep_index = next(i for i, v in enumerate(items) if v.nodeid == dep)
        sorted_items.append(items.pop(dep_index))
        for dep_item in dep_items:
            if dep_item in items:
                sorted_items.append(items.pop(items.index(dep_item)))

    sorted_items.extend(standalone_items)
    items[:] = sorted_items


@pytest.fixture(scope="function", autouse=True)
def case_skip(request, in_data):
    """处理跳过用例"""
    case_data = in_data
    if ast.literal_eval(cache_regular(str(case_data['is_run']))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip(f"Test case {request.node.name} is skipped due to is_run being set to False.")
    else:
        # 检查依赖的用例是否有失败或被跳过的情况
        dependency_marker = request.node.get_closest_marker("dependency")
        if dependency_marker:
            depends = dependency_marker.kwargs.get("depends")
            for dep in depends:
                dep_node = request.session.items.get(dep)
                if dep_node:
                    if dep_node.report_outcome == 'failed':
                        pytest.skip(f"Test case {request.node.name} is skipped due to dependency {dep} failing.")
                    elif dep_node.report_outcome == 'skipped':
                        pytest.skip(f"Test case {request.node.name} is skipped due to dependency {dep} being skipped.")


def pytest_terminal_summary():
    allure_data = AllureFileClean.get_case_count()

    _PASSED = allure_data.get('passed', 0)
    _BROKEN = allure_data.get('broken', 0)
    _FAILED = allure_data.get('failed', 0)
    _SKIPPED = allure_data.get('skipped', 0)
    _TOTAL = allure_data.get('total', 0)
    allure_time = allure_data.get('time', 0)

    INFO.logger.info(f"总用例数: {_TOTAL}")
    INFO.logger.info(f"通过用例数: {_PASSED}")
    ERROR.logger.error(f"异常用例数: {_BROKEN}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info(f"pytest 用例执行总时长: {allure_time} s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info(f"用例成功率: {_RATE:.2f} %")
    except ZeroDivisionError:
        INFO.logger.info("用例成功率: 0.00 %")