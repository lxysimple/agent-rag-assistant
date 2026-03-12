"""
Agent 工具集合。

本模块用于定义 Agent 在执行任务时可调用的工具（Tools），
包括：

1. RAG 知识检索
2. 天气信息查询（示例工具）
3. 用户基础信息获取
4. 外部系统数据查询
5. 报告生成上下文触发工具

所有工具通过 LangChain 的 @tool 装饰器注册，
Agent 在推理过程中可根据需要自动选择调用。
"""

import os
import random

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


# ==============================
# 全局服务实例
# ==============================

rag = RagSummarizeService()


# ==============================
# 模拟用户数据
# ==============================

user_arr = [
    "1001", "1002", "1003", "1004", "1005",
    "1006", "1007", "1008", "1009", "1010",
]

month_arr = [
    "2025-01", "2025-02", "2025-03", "2025-04",
    "2025-05", "2025-06", "2025-07", "2025-08",
    "2025-09", "2025-10", "2025-11", "2025-12",
]


# ==============================
# 外部系统缓存
# ==============================

# 用于缓存 CSV 数据，避免重复读取文件
external_data: dict = {}


# ==============================
# RAG 检索工具
# ==============================

@tool(description="从向量数据库中检索相关知识并返回总结结果")
def rag_summarize(query: str) -> str:
    """调用 RAG 服务进行知识检索与总结。"""
    return rag.rag_summary(query)


# ==============================
# 示例工具：天气查询
# ==============================

@tool(description="获取指定城市的天气信息，返回字符串描述")
def get_weather(city: str) -> str:
    """模拟天气查询接口。"""
    return (
        f"城市{city}天气为晴天，气温10摄氏度，"
        f"空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低"
    )


# ==============================
# 用户信息工具
# ==============================

@tool(description="获取当前用户所在城市名称")
def get_user_location() -> str:
    """随机模拟用户所在城市。"""
    return random.choice(["深圳", "合肥", "杭州"])


@tool(description="获取当前用户 ID")
def get_user_id() -> str:
    """随机模拟用户 ID。"""
    return random.choice(user_arr)


@tool(description="获取当前月份")
def get_current_month() -> str:
    """随机模拟当前月份。"""
    return random.choice(month_arr)


# ==============================
# 外部数据加载
# ==============================

def generate_external_data() -> None:
    """
    从 CSV 文件加载用户使用数据，并缓存至内存。

    数据结构示例：

    external_data = {
        "user_id": {
            "month": {
                "特征": xxx,
                "效率": xxx,
                "耗材": xxx,
                "对比": xxx
            }
        }
    }
    """

    if external_data:
        return

    external_data_path = get_abs_path(agent_config["external_data_path"])

    if not os.path.exists(external_data_path):
        raise FileNotFoundError(f"外部数据文件 {external_data_path} 不存在")

    with open(external_data_path, "r", encoding="utf-8") as f:

        # 跳过 CSV 表头
        lines = f.readlines()[1:]

        for line in lines:
            arr: list[str] = line.strip().split(",")

            user_id = arr[0].replace('"', "")
            feature = arr[1].replace('"', "")
            efficiency = arr[2].replace('"', "")
            consumables = arr[3].replace('"', "")
            comparison = arr[4].replace('"', "")
            time = arr[5].replace('"', "")

            if user_id not in external_data:
                external_data[user_id] = {}

            external_data[user_id][time] = {
                "特征": feature,
                "效率": efficiency,
                "耗材": consumables,
                "对比": comparison,
            }


# ==============================
# 外部系统查询工具
# ==============================

# @tool(description="从外部系统获取用户指定月份的使用记录")
def fetch_external_data(user_id: str, month: str) -> str:
    """
    查询外部系统中的用户使用记录。

    Parameters
    ----------
    user_id : str
        用户 ID
    month : str
        查询月份

    Returns
    -------
    str
        用户使用记录，如果不存在则返回空字符串
    """

    generate_external_data()

    try:
        return str(external_data[user_id][month])
    except KeyError:
        logger.warning(
            f"[fetch_external_data] 未找到用户 {user_id} 在 {month} 的使用记录"
        )
        return ""


# ==============================
# 报告上下文触发工具
# ==============================

@tool(
    description="无参数工具，用于触发报告生成流程，调用后中间件会自动注入上下文信息"
)
def fill_context_for_report():
    """触发报告生成上下文填充。"""
    return "fill_context_for_report 已调用"


if __name__ == "__main__":
    """
    工具函数测试入口。

    运行方式：
        python -m agent.tools.agent_tools

    说明：
        单独测试 fetch_external_data 函数。
        若函数使用了 @tool 装饰器，需要临时注释该装饰器，
        否则 LangChain 会返回 Tool 对象而不是函数结果。
    """

    user_id = "1005"
    month = "2025-01"

    result = fetch_external_data(user_id, month)

    print("=== fetch_external_data Test Result ===")
    print(result)