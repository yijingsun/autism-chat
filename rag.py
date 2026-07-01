"""
RAG 知识库模块
负责从 FAISS 向量库中检索与当前对话相关的特教知识
"""
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import LLM_API_KEY, LLM_BASE_URL, FAISS_INDEX_PATH, TOP_K


def get_embeddings():
    """获取 Embedding 模型（使用 DeepSeek 兼容的 OpenAI 接口）"""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=LLM_API_KEY,
        openai_api_base=f"{LLM_BASE_URL}/v1",
    )


def load_faiss_index():
    """
    加载 FAISS 向量索引
    如果索引不存在，返回 None（此时 RAG 不生效，对话仍可正常运行）
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        print(f"[RAG] FAISS 索引不存在: {FAISS_INDEX_PATH}")
        print("[RAG] 请先运行 python build_knowledge_base.py 构建知识库")
        return None

    embeddings = get_embeddings()
    index = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    print(f"[RAG] FAISS 索引加载成功，共 {index.index.ntotal} 个向量")
    return index


def retrieve_context(query: str, index=None) -> str:
    """
    根据用户输入检索相关知识

    Args:
        query: 用户输入的文本
        index: FAISS 索引实例

    Returns:
        检索到的知识文本，如果索引不存在则返回空字符串
    """
    if index is None:
        return ""

    docs = index.similarity_search(query, k=TOP_K)
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        context_parts.append(f"[{i}] (来源: {source})\n{doc.page_content}")

    return "\n\n".join(context_parts)
