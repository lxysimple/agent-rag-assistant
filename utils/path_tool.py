"""
路径工具模块

用于统一管理项目中的路径问题，主要提供：
1. 获取项目根目录
2. 将项目内相对路径转换为绝对路径

这样可以避免在代码中出现大量硬编码路径，提高代码可移植性。
"""

import os


def get_project_root() -> str:
    """
    获取当前项目的根目录绝对路径。

    原理说明：
    ----------
    __file__ 表示当前 Python 文件的路径，例如：

        /project_root/utils/path_tool.py

    因此可以通过两次 dirname 操作得到项目根目录：

        path_tool.py
            ↓ dirname
        utils/
            ↓ dirname
        project_root/
    """

    # 当前文件的绝对路径，例如：
    # /project_root/utils/path_tool.py
    current_file = os.path.abspath(__file__)

    # 当前文件所在目录，例如：
    # /project_root/utils
    current_dir = os.path.dirname(current_file)

    # 项目根目录，例如：
    # /project_root
    project_root = os.path.dirname(current_dir)

    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    将项目内部的相对路径转换为绝对路径。

    参数：
    -----
    relative_path:
        项目根目录下的相对路径，例如：

            data/example.txt
            config/rag.yml
            logs/agent.log

    返回：
    -----
        对应的绝对路径，例如：

            /project_root/data/example.txt
    """

    project_root = get_project_root()

    # 使用 os.path.join 拼接路径，保证跨平台兼容
    return os.path.join(project_root, relative_path)


if __name__ == "__main__":

    # 模块测试
    # 运行方式：
    # python -m utils.path_tool

    example_path = get_abs_path("data/维护保养.txt")

    print("项目根目录：", get_project_root())
    print("示例文件路径：", example_path)