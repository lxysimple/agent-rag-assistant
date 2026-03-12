from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.chat_models.tongyi import BaseChatModel, ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings

from utils.config_handler import rag_config


class BaseModelFactory(ABC):
    """
    模型工厂抽象基类。

    作用：
    统一模型创建入口，使上层业务代码不依赖具体模型实现，
    方便未来进行模型替换、扩展或增加多模型支持。
    """

    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        生成模型实例。

        Returns
        -------
        Embeddings | BaseChatModel
            返回具体的 Embedding 模型或 Chat 模型实例
        """
        raise NotImplementedError


class ChatModelFactory(BaseModelFactory):
    """
    聊天模型工厂。

    根据配置文件中的模型名称创建对应的大语言模型实例。
    """

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        创建聊天模型实例。

        当前默认使用 Tongyi 大模型。
        如果未来需要支持 OpenAI、Qwen、DeepSeek 等模型，
        只需在此处增加分支逻辑即可，无需修改业务代码。
        """
        return ChatTongyi(model=rag_config["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    """
    Embedding 模型工厂。

    用于创建文本向量化模型实例，
    主要用于 RAG 系统中的向量检索。
    """

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """
        创建 Embedding 模型实例。
        """
        return DashScopeEmbeddings(
            model=rag_config["embedding_model_name"]
        )


# =========================
# 对外暴露的模型实例
# =========================

# 聊天模型实例（用于 Agent / RAG 推理）
chat_model = ChatModelFactory().generator()

# 向量模型实例（用于向量数据库 embedding）
embedding_model = EmbeddingsFactory().generator()