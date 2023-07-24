import os, shutil
from common.setting import ensure_path_sep


'''
删除test_case目录下所有已经生成的用例
'''

def del_directories(path):
    """删除目录下的所有文件夹，排除__init__.py和conftest.py文件"""
    if not os.path.isdir(path):
        return

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not (dir == "venv"):
                shutil.rmtree(dir_path)

        # 保留__init__和conftest
        for file in files:
            file_path = os.path.join(root, file)
            if not (file == "__init__.py" or file == "conftest.py"):
                os.remove(file_path)

if __name__ == '__main__':
    directory = ensure_path_sep("\\test_case")
    del_directories(directory)