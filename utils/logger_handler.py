"""
日志工具模块

统一提供项目日志记录能力：
- 控制台日志输出
- 文件日志保存
- 统一日志格式

项目中所有模块建议通过 get_logger(__name__) 获取 logger，
这样日志中会自动记录模块来源，方便定位问题。
"""

import logging
import os
from typing import Optional
from datetime import datetime

from utils.path_tool import get_abs_path


# ==============================
# 日志保存根目录
# ==============================

# 日志文件统一保存在项目 logs 目录下
LOG_ROOT = get_abs_path("logs")

# 确保日志目录存在，如果不存在则自动创建
os.makedirs(LOG_ROOT, exist_ok=True)


# ==============================
# 日志格式配置
# ==============================

# 日志输出格式：
# 时间 - logger名称 - 日志级别 - 文件名:行号 - 日志内容
#
# 示例：
# 2026-03-04 13:31:41,240 - agent.utils.logger_handler - DEBUG - test.py:3 - 这是一条 DEBUG 日志
DEFAULT_LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)


def get_logger(
    name: str = "agent",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    获取一个已经按项目标准配置好的 logger。

    参数说明：
    ----------
    name:
        logger 名称。实际项目中推荐在各业务模块中显式写：

            get_logger(__name__)

        这样日志中会带有完整模块路径，例如：
            rag.rag_service
            agent.agent_core
            utils.file_tool

        便于在日志系统中快速定位问题来源。

    console_level:
        控制台日志输出级别（默认 INFO）。
        也就是说只有 >=INFO 级别的日志才会打印到终端。

    file_level:
        文件日志级别（默认 DEBUG）。
        文件日志通常记录更详细的信息，用于排查问题。

    log_file:
        指定日志文件路径。如果为 None，则自动按照
        "logger名称 + 日期" 的方式生成日志文件，例如：

            logs/agent_20260312.log
    """

    # 如果全局已经存在同名 logger，则直接复用
    logger = logging.getLogger(name)

    # 顶层 logger 级别设置为 DEBUG，具体输出由各 handler 控制
    logger.setLevel(logging.DEBUG)

    # 防止日志向 root logger 传播，避免重复输出
    logger.propagate = False

    # 如果 logger 已经配置过 handler，则直接返回
    # 否则多个模块 import 本文件并调用 get_logger 时
    # 会重复添加 handler，导致一条日志打印多次
    if logger.handlers:
        return logger

    # ==============================
    # 1. 控制台 Handler
    # ==============================

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMATTER)

    logger.addHandler(console_handler)

    # ==============================
    # 2. 文件 Handler
    # ==============================

    # 如果没有指定日志文件，则自动生成
    if log_file is None:
        today = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(LOG_ROOT, f"{name}_{today}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMATTER)

    # 此时 logger 中会有两个 handler：
    # 1. 控制台输出
    # 2. 文件日志记录
    logger.addHandler(file_handler)

    return logger


# ==============================
# 默认 logger
# ==============================

# 直接 import 本模块即可使用：
#
# from utils.logger_handler import logger
#
# logger.info("xxx")
logger = get_logger()


if __name__ == "__main__":
    # 模块测试
    # 运行方式：
    # python -m utils.logger_handler

    test_logger = get_logger(__name__)

    test_logger.debug("这是一条 DEBUG 日志（默认只写入文件）。")
    test_logger.info("这是一条 INFO 日志。")
    test_logger.warning("这是一条 WARNING 日志。")
    test_logger.error("这是一条 ERROR 日志。")