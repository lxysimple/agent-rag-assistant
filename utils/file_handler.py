"""
文件工具模块

提供以下功能：
- 文件 MD5 计算
- 指定类型文件扫描
- 文档加载（PDF / TXT）
"""

import hashlib
import os
from typing import List, Tuple, Optional

from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str) -> str:
    """
    计算文件内容的 MD5 十六进制字符串。

    Args:
        filepath: 文件路径

    Returns:
        MD5 十六进制字符串；如果文件不存在或读取失败返回 ""。
    """

    if not os.path.exists(filepath):
        logger.error(f"[MD5] 文件不存在: {filepath}")
        return ""

    if not os.path.isfile(filepath):
        logger.error(f"[MD5] 路径不是文件: {filepath}")
        return ""

    md5_obj = hashlib.md5()
    chunk_size = 4096  # 4KB 分块读取，避免大文件占用过多内存

    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):  # Python3.8+ 海象运算符
                md5_obj.update(chunk)

        return md5_obj.hexdigest()

    except Exception as e:
        logger.error(f"[MD5] 计算失败: {filepath}, error={e}")
        return ""


def listdir_with_allowed_type(
    path: str,
    allowed_types: Tuple[str, ...],
) -> Tuple[str, ...]:
    """
    列出目录中指定后缀的文件（非递归）。

    Args:
        path: 目录路径
        allowed_types: 允许的文件后缀，例如 (".txt", ".pdf")

    Returns:
        文件绝对路径 tuple，如异常返回空 tuple
    """

    if not os.path.isdir(path):
        logger.warning(f"[listdir] 非目录路径: {path}")
        return tuple()

    files: List[str] = []

    try:
        for name in os.listdir(path):
            if name.lower().endswith(allowed_types):
                files.append(os.path.join(path, name))

        return tuple(files)

    except Exception as e:
        logger.error(f"[listdir] 读取目录失败: {path}, error={e}")
        return tuple()


def pdf_loader(
    filepath: str,
    passwd: Optional[str] = None,
) -> List[Document]:
    """
    使用 LangChain PyPDFLoader 加载 PDF 文档。

    Args:
        filepath: PDF 文件路径
        passwd: PDF 密码（如无则为 None）

    Returns:
        Document 列表
    """
    try:
        loader = PyPDFLoader(file_path=filepath, password=passwd)
        return loader.load()

    except Exception as e:
        logger.error(f"[PDF Loader] 加载失败: {filepath}, error={e}")
        return []


def txt_loader(filepath: str) -> List[Document]:
    """
    使用 LangChain TextLoader 加载 TXT 文档。

    Args:
        filepath: 文本文件路径

    Returns:
        Document 列表
    """
    try:
        loader = TextLoader(filepath, encoding="utf-8")
        return loader.load()

    except Exception as e:
        logger.error(f"[TXT Loader] 加载失败: {filepath}, error={e}")
        return []