
from common.setting import ensure_path_sep
from utils.read_files_tools.clean_case import del_directories
from run import run

directory = ensure_path_sep("\\test_case")
del_directories(directory)
run()
