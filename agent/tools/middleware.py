"""
Agent Middleware 中间件。

本模块用于扩展 Agent 的执行流程，包括：

1. Tool 调用监控
2. 模型调用日志
3. 动态 Prompt 切换

通过 LangChain / LangGraph 的 middleware 机制，
可以在 Agent 执行流程中的关键节点插入自定义逻辑。
"""

from typing import Callable

from langchain.agents.middleware import before_model, wrap_tool_call, dynamic_prompt
from langchain.agents.middleware import ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompts, load_report_prompts


# ======================================================
# Tool 调用监控中间件
# ======================================================

@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """
    Tool 调用监控。

    在 Tool 执行前后记录日志，并在特定工具触发时
    修改 Agent 运行时上下文。

    Parameters
    ----------
    request : ToolCallRequest
        当前 Tool 调用请求对象
    handler : Callable
        底层 Tool 执行函数

    Returns
    -------
    ToolMessage | Command
        Tool 执行结果
    """

    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    logger.info(f"[tool_monitor] 调用工具: {tool_name}")
    logger.info(f"[tool_monitor] 参数: {tool_args}")

    try:
        # 调用真实 Tool
        result = handler(request)

        logger.info(f"[tool_monitor] 工具 {tool_name} 调用成功")

        # 特殊工具触发上下文修改
        if tool_name == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result

    except Exception as e:
        logger.error(
            f"[tool_monitor] 工具 {tool_name} 调用失败: {str(e)}",
            exc_info=True,
        )
        raise


# ======================================================
# 模型调用前日志
# ======================================================

@before_model
def log_before_model(
    state: AgentState,
    runtime: Runtime,
):
    """
    在模型调用前记录日志。

    Parameters
    ----------
    state : AgentState
        Agent 当前状态（包含历史消息等）
    runtime : Runtime
        Agent 运行时上下文
    """

    message_count = len(state["messages"])

    logger.info(
        f"[before_model] 即将调用模型，当前消息数量: {message_count}"
    )

    # 输出最后一条消息（调试用）
    last_message = state["messages"][-1]

    logger.debug(
        f"[before_model] {type(last_message).__name__} | {last_message.content}"
    )

    return None


# ======================================================
# Prompt 动态切换
# ======================================================

@dynamic_prompt
def report_prompt_switch(
    request: ModelRequest,
):
    """
    动态 Prompt 切换。

    在每次模型调用前，根据 runtime.context 中的标志
    决定使用哪个 Prompt 模板。

    当前逻辑：
    - report=False -> 使用系统默认 Prompt
    - report=True  -> 使用报告生成 Prompt
    """

    is_report = request.runtime.context.get("report", False)

    if is_report:
        logger.info("[prompt_switch] 切换为报告生成 Prompt")
        return load_report_prompts()

    return load_system_prompts()