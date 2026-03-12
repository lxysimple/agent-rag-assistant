"""
RAG 总结服务

功能说明：
用户输入问题 -> 检索向量数据库中的相关文档 -> 
将问题与检索到的参考资料一起提交给 LLM ->
由模型生成最终总结回答。

整体流程：
User Question
      ↓
Vector Retriever
      ↓
Context 构建
      ↓
Prompt Template
      ↓
LLM
      ↓
Answer
"""

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts.base import PromptValue

from model.factory import chat_model


class RagSummarizeService:
    """
    RAG 总结服务类

    负责：
    1. 检索相关文档
    2. 构建上下文
    3. 调用 LLM 生成回答
    """

    def __init__(self) -> None:

        # 向量数据库服务
        self.vector_store = VectorStoreService()

        # 获取 retriever（用于语义检索）
        self.retriever = self.vector_store.get_retriever()

        # 加载 RAG Prompt 模板
        self.prompt_text = load_rag_prompts()

        # 构建 PromptTemplate
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)

        # 初始化 LLM
        self.model = chat_model

        # 初始化 LangChain Chain
        self.chain = self._init_chain()

    def _init_chain(self):
        """
        构建 LangChain 推理链。

        Chain结构：
        PromptTemplate -> LLM -> OutputParser
        """

        def print_prompt(prompt: PromptValue) -> PromptValue:
            """
            调试函数：打印最终 Prompt（调试 RAG 时非常有用）。
            """
            # print("--" * 20)
            # print(prompt.to_string())
            # print("--" * 20)
            return prompt

        chain = (
            self.prompt_template
            | print_prompt
            | self.model
            | StrOutputParser()
        )

        return chain

    def retrieve_docs(self, query: str) -> list[Document]:
        """
        根据用户问题检索相关文档。

        Args:
            query: 用户问题

        Returns:
            检索到的 Document 列表
        """
        return self.retriever.invoke(query)

    def rag_summary(self, question: str) -> str:
        """
        执行完整的 RAG 推理流程。

        步骤：
        1. 检索相关文档
        2. 构建上下文
        3. 调用 LLM 生成回答
        """

        documents = self.retrieve_docs(question)

        # 构建 RAG context
        context = ""
        for idx, doc in enumerate(documents, start=1):
            context += (
                f"\n参考内容{idx}: {doc.page_content}; "
                f"元数据: {doc.metadata}\n"
            )

        # 调用 Chain
        return self.chain.invoke(
            {
                "context": context,
                "input": question,
            }
        )


if __name__ == "__main__":

    # 模块测试
    # 运行方式：
    # python -m rag.rag_service

    service = RagSummarizeService()

    result = service.rag_summary("小户型适合哪些扫地机器人")

    print(result)