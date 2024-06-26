#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
from enum import Enum, unique
from typing import Text, Dict, Callable, Union, Optional, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator


# =========================
# 枚举类
# =========================

@unique
class NotificationType(Enum):
    """ 自动化通知方式 """
    DEFAULT = ('0', "默认通知类型")
    FEI_SHU = ('1', "飞书")
    DING_TALK = ('2', "钉钉")
    WECHAT = ('3', "微信")
    EMAIL = ('4', "Email")


@unique
class RequestType(Enum):
    """ request请求发送，请求参数的数据类型 """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


@unique
class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTION = "OPTION"


@unique
class DependentType(Enum):
    """ 数据依赖相关枚举 """
    RESPONSE = 'response'
    REQUEST = 'request'
    SQL_DATA = 'sqlData'
    CACHE = "cache"


@unique
class AllureAttachmentType(Enum):
    """ allure 报告的文件类型枚举 """
    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"
    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"
    PDF = "pdf"


@unique
class AssertMethod(Enum):
    """断言类型"""
    equals = "=="
    less_than = "lt"
    less_than_or_equals = "le"
    greater_than = "gt"
    greater_than_or_equals = "ge"
    not_equals = "not_eq"
    string_equals = "str_eq"
    length_equals = "len_eq"
    length_greater_than = "len_gt"
    length_greater_than_or_equals = 'len_ge'
    length_less_than = "len_lt"
    length_less_than_or_equals = 'len_le'
    contains = "contains"
    contained_by = 'contained_by'
    startswith = 'startswith'
    endswith = 'endswith'


@unique
class TestCaseEnum(Enum):
    URL = ("url", True)
    HOST = ("host", True)
    METHOD = ("method", True)
    DETAIL = ("detail", True)
    IS_RUN = ("is_run", True)
    HEADERS = ("headers", True)
    REQUEST_TYPE = ("requestType", True)
    DATA = ("data", True)
    DE_CASE = ("dependence_case", True)
    DE_CASE_DATA = ("dependence_case_data", False)
    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    SQL = ("sql", False)
    ASSERT_DATA = ("assert", True)
    SETUP_SQL = ("setup_sql", False)
    TEARDOWN = ("teardown", False)
    TEARDOWN_SQL = ("teardown_sql", False)
    SLEEP = ("sleep", False)


# =========================
# 数据类
# =========================

@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text

    def __str__(self):
        return f"TestMetrics(passed={self.passed}, failed={self.failed}, broken={self.broken}, skipped={self.skipped}, total={self.total}, pass_rate={self.pass_rate}, time={self.time})"

# =========================
# 工具函数
# =========================

def load_module_functions(module) -> Dict[Text, Callable]:
    """ 获取 module中方法的名称和所在的内存地址 """
    module_functions = {}
    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


# =========================
# Pydantic 模型
# =========================

class Assert(BaseModel):
    jsonpath: Text
    type: Text
    value: Any
    AssertType: Optional[Text] = None


class DependentData(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text] = None
    replace_key: Optional[Text] = None


class DependentCaseData(BaseModel):
    case_id: Text
    dependent_data: Optional[List[DependentData]] = Field(default=[])


class ParamPrepare(BaseModel):
    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text] = None


class SendRequest(BaseModel):
    dependent_type: Text
    jsonpath: Optional[Text] = None
    cache_data: Optional[Text] = None
    set_cache: Optional[Text] = None
    replace_key: Optional[Text] = None


class TearDown(BaseModel):
    case_id: Text
    param_prepare: Optional[List[ParamPrepare]] = Field(default=[])
    send_request: Optional[List[SendRequest]] = Field(default=[])


class CurrentRequestSetCache(BaseModel):
    type: Text
    jsonpath: Text
    name: Text


class TestCase(BaseModel):
    url: Text
    method: Text
    detail: Text
    assert_data: Union[Dict, Text]
    headers: Optional[Union[Dict[str, str], str]] = None
    requestType: Text
    is_run: Optional[Union[bool, Text]] = None
    data: Any = None
    dependence_case: Optional[bool] = False
    dependence_case_data: Optional[Union[None, List[DependentCaseData], Text]] = Field(default=[])
    sql: Optional[List[str]] = Field(default=[])
    setup_sql: Optional[List[str]] = Field(default=[])
    status_code: Optional[int] = None
    teardown_sql: Optional[List] = None
    teardown: Optional[List[TearDown]] = Field(default=[])
    current_request_set_cache: Optional[List[CurrentRequestSetCache]] = Field(default=[])
    sleep: Optional[Union[int, float]]


class ResponseData(BaseModel):
    url: Text
    is_run: Optional[Union[bool, Text]]
    detail: Text
    response_data: Text
    request_body: Any
    method: Text
    sql_data: Dict
    yaml_data: "TestCase"
    headers: Dict
    cookie: Dict
    assert_data: Dict
    res_time: Union[int, float]
    status_code: int
    teardown: Optional[List[TearDown]] = None
    teardown_sql: Optional[List]
    body: Any


class DingTalk(BaseModel):
    webhook: Optional[Text]
    secret: Optional[Text]


class MySqlDB(BaseModel):
    switch: bool = False
    host: Optional[Text] = None
    user: Optional[Text] = None
    password: Optional[Text] = None
    port: Optional[int] = 3306


class Lark(BaseModel):
    webhook: Optional[Text]
    user_id: List[Text]


class Webhook(BaseModel):
    webhook: Optional[Text]


class Email(BaseModel):
    send_user: Optional[Text]
    email_host: Optional[Text]
    stamp_key: Optional[Text]
    send_list: Optional[Text]


class Config(BaseModel):
    project_name: Text
    env: Text
    tester_name: Text
    use_xdist: bool = False
    notification_type: Union[Text, int, list] = '0'
    excel_report: bool
    ding_talk: Optional[DingTalk] = None
    mysql_db: Optional[MySqlDB] = None
    mirror_source: Text
    wechat: Optional[Webhook] = None
    email: Optional[Email] = None
    lark: Optional[Lark] = None
    real_time_update_test_cases: bool = False
    host: Text
    app_host: Optional[Text]

    @validator('notification_type', pre=True, always=True)
    def validate_notification_type(cls, v):
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid type for notification_type")