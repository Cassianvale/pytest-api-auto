
from common.setting import ensure_path_sep
from utils.read_files_tools.clean_case import del_directories
from run import run

if __name__ == '__main__':
    # 清空test_case目录下所有已经生成的用例
    directory = ensure_path_sep("\\test_case")
    del_directories(directory)
    run()