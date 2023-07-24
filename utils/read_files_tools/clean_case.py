import os
from utils.read_files_tools.clean_files import del_file
from common.setting import ensure_path_sep

directory = ensure_path_sep("\\test_case")

del_file(directory)