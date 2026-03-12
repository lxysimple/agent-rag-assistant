"""
项目 Web 启动入口

该模块基于 Streamlit 构建项目的 Web 交互界面，用于接收用户问题并展示模型返回结果。

系统整体流程如下：
1. 用户在网页端输入问题
2. 问题发送至 Agent
3. Agent 基于预设的 Prompt 模板进行推理与决策
4. 根据任务需求选择性调用工具函数（Tool）获取实时数据
5. 结合 RAG（Retrieval-Augmented Generation）技术，从向量数据库中检索相关知识
6. 将工具结果与检索内容整合后发送给 LLM 进行生成
7. 最终结果返回至前端页面展示给用户

运行方式：
    streamlit run app.py
"""

import streamlit as st
from agent.react_agent import ReactAgent
import time


st.title("智能客服")  # 添加网页标题
st.divider()  # 分隔符: 一道横线


# 初始化 Agent（只在第一次进入页面时创建）
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

# 初始化历史消息记录
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# 将历史对话展示
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])


# 用户输入栏
user_prompt = st.chat_input()

if user_prompt:

    # 在页面输出用户的提问，类似 chatgpt 显示的提问
    st.chat_message("user").write(user_prompt)

    with st.spinner("AI思考中..."):  # 增加用户体验, 在 spinner 内的代码执行中, 会有转圈动画
        time.sleep(1)

        # 调用 Agent 执行流式响应
        response_stream = st.session_state["agent"].execute_stream(user_prompt)

        response_cache = []

        def capture(generator):
            for chunk in generator:
                response_cache.append(chunk)

                for char in chunk:  # 一个一个字符返回
                    time.sleep(0.01)  # 不设置暂停时间返回太快了, 等价于一下返回一段

                    # yield = 暂停函数执行，并把一个值“产出”出去，下次调用该函数还能从暂停的位置继续执行。
                    yield char

        # write_stream 会逐步消费生成器中的内容
        # 如果直接传入原始 stream，内容在输出后就会被消费，无法再次获取
        # 因此通过 capture() 对 stream 进行封装，在流式输出的同时保存完整结果
        st.chat_message("assistant").write_stream(capture(response_stream))


    # 添加当前对话进历史记录队列
    st.session_state["messages"].append({
        "role": "user",
        "content": user_prompt
    })

    st.session_state["messages"].append({
        "role": "assistant",
        "content": response_cache[-1]  # 忽略过程信息, 只记录最后一条结果项
    })


    st.rerun()  # 刷新页面, 清除 AI 执行 ReAct 过程记录, 直接展示历史记录中记录的结果

    