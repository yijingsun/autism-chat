"""
知识库构建脚本
将 data/knowledge/ 目录下的文本文件切分、向量化，存入 FAISS 索引

运行方式：
    python build_knowledge_base.py

前置条件：
    1. 在 data/knowledge/ 目录下放入 .txt 文件（特教相关资料）
    2. 已安装 sentence-transformers（本地 Embedding 模型，无需 API Key）
"""
import os
import glob
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import (
    KNOWLEDGE_DIR, FAISS_INDEX_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP,
)


def load_documents() -> list[Document]:
    """加载 data/knowledge/ 目录下的所有 .txt 文件"""
    txt_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.txt"))

    if not txt_files:
        print(f"[警告] {KNOWLEDGE_DIR} 目录下没有找到 .txt 文件")
        print("[提示] 请先放入特教相关资料（纯文本格式）")
        return []

    documents = []
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if content:
            doc = Document(page_content=content, metadata={"source": filename})
            documents.append(doc)
            print(f"  已加载: {filename} ({len(content)} 字符)")

    print(f"[完成] 共加载 {len(documents)} 个文档")
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """将文档切分为适合向量化的块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", ".", " "],
    )

    chunks = splitter.split_documents(documents)
    print(f"[完成] 文档切分为 {len(chunks)} 个块")
    return chunks


def build_and_save_index(chunks: list[Document]):
    """构建 FAISS 索引并保存到本地"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    print("[进行中] 正在构建 FAISS 索引（使用本地 HuggingFace Embedding 模型）...")
    index = FAISS.from_documents(chunks, embeddings)

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    index.save_local(FAISS_INDEX_PATH)
    print(f"[完成] FAISS 索引已保存到: {FAISS_INDEX_PATH}")
    print(f"[信息] 索引包含 {index.index.ntotal} 个向量")


def main():
    print("=" * 50)
    print("自闭症友好对话系统 - 知识库构建")
    print("=" * 50)

    # 1. 加载文档
    documents = load_documents()
    if not documents:
        return

    # 2. 切分文档
    chunks = split_documents(documents)

    # 3. 构建并保存索引
    build_and_save_index(chunks)

    print("\n[全部完成] 知识库构建成功！现在可以启动 app.py 使用 RAG 功能。")


if __name__ == "__main__":
    main()
