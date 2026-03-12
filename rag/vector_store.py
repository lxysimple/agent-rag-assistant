"""
向量库服务封装（Vector Store Service）

职责：
1. 管理向量数据库（Chroma）
2. 扫描知识库文件
3. 文档切分
4. 文档向量化并写入向量库
5. 基于 MD5 的文件去重

对外暴露接口：
- get_retriever(): 获取检索器
- load_document(): 扫描数据目录并导入新文档
"""

import os
from typing import List, Iterable

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils.config_handler import chroma_config
from utils.path_tool import get_abs_path
from utils.file_handler import (
    pdf_loader,
    txt_loader,
    listdir_with_allowed_type,
    get_file_md5_hex,
)
from utils.logger_handler import logger
from model.factory import embedding_model


class VectorStoreService:
    """
    向量库服务类
    """

    def __init__(self) -> None:

        # =========================
        # 初始化向量数据库
        # =========================
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embedding_model,
            persist_directory=chroma_config["persist_directory"],
        )

        # =========================
        # 文本切分器
        # =========================
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function=len,
        )

        # MD5 记录文件
        self.md5_store_path = get_abs_path(chroma_config["md5_hex_store"])

    # =========================
    # 对外接口
    # =========================

    def get_retriever(self):
        """
        获取向量检索器
        """
        return self.vector_store.as_retriever(
            search_kwargs={"k": chroma_config["k"]}
        )

    # =========================
    # MD5 相关工具
    # =========================

    def _check_md5(self, md5_str: str) -> bool:
        """
        检查 MD5 是否已经记录（用于防止重复加载知识库）
        """

        if not os.path.exists(self.md5_store_path):
            # 如果文件不存在，则创建空文件
            open(self.md5_store_path, "w", encoding="utf-8").close()
            return False

        with open(self.md5_store_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == md5_str:
                    return True

        return False

    def _save_md5(self, md5_str: str) -> None:
        """
        保存 MD5 记录
        """

        with open(self.md5_store_path, "a", encoding="utf-8") as f:
            f.write(md5_str + "\n")

    # =========================
    # 文件读取
    # =========================

    def _load_file_documents(self, filepath: str) -> List[Document]:
        """
        根据文件类型选择对应 loader
        """

        if filepath.endswith(".txt"):
            return txt_loader(filepath)

        if filepath.endswith(".pdf"):
            return pdf_loader(filepath)

        return []

    # =========================
    # 知识库加载
    # =========================

    def load_document(self) -> None:
        """
        从数据目录加载文档并写入向量库（按文件 MD5 去重）
        """

        data_dir = get_abs_path(chroma_config["data_path"])

        allowed_files: List[str] = listdir_with_allowed_type(
            data_dir,
            tuple(chroma_config["allow_knowledge_file_type"]),
        )

        for filepath in allowed_files:

            # 计算文件 MD5，用于去重
            md5_hex = get_file_md5_hex(filepath)

            if self._check_md5(md5_hex):
                logger.info(f"[知识库加载] {filepath} 已存在，跳过")
                continue

            try:
                documents = self._load_file_documents(filepath)

                if not documents:
                    logger.warning(f"[知识库加载] {filepath} 无有效文本内容，跳过")
                    continue

                # 文本切分
                split_docs = self.splitter.split_documents(documents)

                if not split_docs:
                    logger.warning(f"[知识库加载] {filepath} 分片后无有效内容，跳过")
                    continue

                # 写入向量库
                self.vector_store.add_documents(split_docs)

                # 保存 MD5
                self._save_md5(md5_hex)

                logger.info(
                    f"[知识库加载] {filepath} 加载成功，分片数量: {len(split_docs)}"
                )

            except Exception as e:  # noqa: BLE001
                logger.error(
                    f"[知识库加载] {filepath} 加载失败: {str(e)}",
                    exc_info=True,
                )

    # =========================
    # 模块测试
    # =========================


if __name__ == "__main__":

    # python -m rag.vector_store

    vs = VectorStoreService()

    # 加载知识库
    vs.load_document()

    # 测试检索
    retriever = vs.get_retriever()

    results: Iterable[Document] = retriever.invoke("迷路")

    for r in results:
        print("===" * 20)
        print(r.page_content)
        print("===" * 20)