import os
import json
from typing import Any, Text, Union
from common.setting import ensure_path_sep
from utils.other_tools.exceptions import ValueNotFoundError

class Cache:
    def __init__(self, filename: Union[Text, None] = None) -> None:
        self.cache_dir = ensure_path_sep("\\cache\\")
        # 校验cache文件夹
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        # 如果filename不为空，则操作指定文件内容
        if filename:
            self.path = os.path.join(self.cache_dir, f"{filename}.json")
        # 如果filename为None，则操作所有文件内容
        else:
            self.path = self.cache_dir

    def set_cache(self, key: Text, value: Any) -> None:
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump({key: value}, file, indent=4, ensure_ascii=False)

    def set_caches(self, value: Any) -> None:
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(value, file, indent=4, ensure_ascii=False)

    def get_cache(self) -> Any:
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    def clean_cache(self) -> None:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"您要删除的缓存文件不存在 {self.path}")
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls) -> None:
        cache_path = ensure_path_sep("\\cache")

        # 列出目录下所有文件，生成一个list
        list_dir = os.listdir(cache_path)
        for i in list_dir:
            # 循环删除文件夹下得所有内容
            os.remove(os.path.join(cache_path, i))

_cache_config = {}

class CacheHandler:
    @staticmethod
    def get_cache(cache_data):
        try:
            return _cache_config[cache_data]
        except KeyError:
            raise ValueNotFoundError(f"{cache_data}的缓存数据未找到，请检查是否将该数据存入缓存中")

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache_config[cache_name] = value
