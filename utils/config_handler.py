"""
配置文件加载工具

负责读取项目中的 YAML 配置文件，并解析为 Python 字典对象，
供 RAG、Agent、向量数据库等模块使用。
"""

import yaml
from typing import Dict, Any
from utils.path_tool import get_abs_path


def _load_yaml_config(
    config_path: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    通用 YAML 配置加载函数

    Args:
        config_path: YAML 文件路径
        encoding: 文件编码

    Returns:
        解析后的 Python 字典对象
    """
    with open(config_path, "r", encoding=encoding) as f:
        # safe_load 更安全，避免执行 YAML 中的任意 Python 对象
        return yaml.safe_load(f)


def load_rag_config(
    config_path: str = get_abs_path("config/rag.yml"),
    encoding: str = "utf-8",
):
    """读取 RAG 系统相关配置"""
    return _load_yaml_config(config_path, encoding)


def load_chroma_config(
    config_path: str = get_abs_path("config/chroma.yml"),
    encoding: str = "utf-8",
):
    """读取本地向量数据库（Chroma）配置"""
    return _load_yaml_config(config_path, encoding)


def load_prompts_config(
    config_path: str = get_abs_path("config/prompts.yml"),
    encoding: str = "utf-8",
):
    """读取提示词模板配置"""
    return _load_yaml_config(config_path, encoding)


def load_agent_config(
    config_path: str = get_abs_path("config/agent.yml"),
    encoding: str = "utf-8",
):
    """读取 Agent 相关配置"""
    return _load_yaml_config(config_path, encoding)


# ==============================
# 加载配置（模块初始化时执行）
# ==============================

rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()


if __name__ == "__main__":  # 模块测试
    # python -m utils.config_handler
    print(rag_config["chat_model_name"])