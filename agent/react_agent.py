"""
ReAct Agent 封装类。

负责初始化 Agent 并提供流式执行接口。

核心能力：
1. 调用大语言模型进行推理
2. 调用工具（Tools）获取外部信息
3. 通过 Middleware 扩展 Agent 执行流程
4. 支持流式返回结果（Streaming）
"""

from typing import Generator

from langchain.agents import create_agent

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts

from agent.tools.agent_tools import (
    rag_summarize,
    get_weather,
    get_user_location,
    get_user_id,
    get_current_month,
    fetch_external_data,
    fill_context_for_report,
)

from agent.tools.middleware import (
    monitor_tool,
    log_before_model,
    report_prompt_switch,
)


class ReactAgent:
    """ReAct Agent 封装类"""

    def __init__(self) -> None:
        """初始化 Agent"""

        # 工具列表
        tools = [
            rag_summarize,
            get_weather,
            get_user_location,
            get_user_id,
            get_current_month,
            fetch_external_data,
            fill_context_for_report,
        ]

        # 中间件列表
        middleware = [
            monitor_tool,
            log_before_model,
            report_prompt_switch,
        ]

        # 创建 Agent
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=tools,
            middleware=middleware,
        )

    def execute_stream(self, query: str) -> Generator[str, None, None]:
        """
        执行 Agent 并以流式方式返回结果。

        Parameters
        ----------
        query : str
            用户输入问题

        Yields
        ------
        str
            模型生成的文本片段
        """

        input_dict = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }

        stream = self.agent.stream(
            input_dict,
            stream_mode="values",
            context={"report": False},
        )

        for chunk in stream:
            # 取当前最新消息
            latest_message = chunk["messages"][-1]

            content = latest_message.content.strip()

            if content:
                yield content + "\n"

if __name__ == "__main__":
    """
    模块测试入口。

    运行方式：
        python -m agent.react_agent

    功能：
        1. 初始化 ReactAgent
        2. 发送测试问题
        3. 以流式方式打印 Agent 返回结果
    """

    # 初始化 Agent
    agent = ReactAgent()

    # 测试问题示例
    query_weather = "扫地机器人在我所在的地区的气温下如何保养"
    query_report = "给我生成我的使用报告"

    # 选择测试问题
    query = query_report

    print("\n===== Agent Response =====\n")

    # 流式输出 Agent 回复
    for chunk in agent.execute_stream(query):
        print(chunk, end="", flush=True)

    print("\n\n===== End =====")