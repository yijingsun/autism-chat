"""
项目配置文件
所有可配置的参数集中管理，方便修改和扩展
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# LLM 配置
# ============================================================
# 支持任何 OpenAI 兼容的 API（DeepSeek、OpenAI、Qwen 等）
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "deepseek-chat")

# ============================================================
# RAG 配置
# ============================================================
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "data", "knowledge")
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "data", "faiss_index")
CHUNK_SIZE = 500        # 文本切分大小（字符数）
CHUNK_OVERLAP = 50      # 切分重叠大小
TOP_K = 3               # 检索返回的文档块数量

# ============================================================
# 对话配置
# ============================================================
MAX_HISTORY_TURNS = 10  # 保留的最大对话轮数（自闭症儿童注意力有限，控制上下文长度）

# ============================================================
# 情绪关键词
# ============================================================
EMOTION_KEYWORDS = {
    "negative": [
        "不开心", "不高兴", "害怕", "生气", "难过", "不想",
        "不要", "讨厌", "哭", "痛", "累", "饿",
        "害怕", " scared", "angry", "sad",
    ],
    "positive": [
        "开心", "高兴", "喜欢", "好玩", "棒", "厉害",
        "谢谢", "哈哈", "笑", "快乐",
        "happy", "like", "fun", "good",
    ],
}
