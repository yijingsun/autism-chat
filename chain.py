"""
对话链模块
组装 LangChain 对话链：System Prompt + 情绪检测 + RAG + 对话记忆
"""
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME, MAX_HISTORY_TURNS
from prompts import SYSTEM_PROMPT, EMOTION_HINTS
from emotion import detect_emotion
from rag import retrieve_context


def get_llm() -> ChatOpenAI:
    """获取 LLM 实例（模型无关设计，可切换任意 OpenAI 兼容模型）"""
    return ChatOpenAI(
        model=LLM_MODEL_NAME,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        temperature=0.7,
        max_tokens=600,  # 允许更充实的回复，避免屏幕空旷
    )


# 全局 LLM 和 FAISS 索引（懒初始化）
_llm = None
_faiss_index = None


def init_chain(faiss_idx=None):
    """初始化对话链"""
    global _llm, _faiss_index
    _llm = get_llm()
    _faiss_index = faiss_idx


def _ensure_initialized():
    """确保 LLM 已初始化（懒加载）"""
    global _llm
    if _llm is None:
        print("[chain] 懒初始化 LLM...", flush=True)
        _llm = get_llm()


def chat(user_input: str, history: list = None, topic_hint: str = "") -> str:
    """
    处理一轮对话（无状态，由 Chainlit 管理历史）

    Args:
        user_input: 用户输入
        history: Chainlit 传入的对话历史 (messages 格式)
        topic_hint: 可选的话题引导提示（如“打招呼”“数数游戏”等）

    Returns:
        模型回复文本
    """
    # 1. 情绪检测
    emotion = detect_emotion(user_input)
    emotion_hint = EMOTION_HINTS.get(emotion, "")

    # 2. RAG 检索
    context = retrieve_context(user_input, _faiss_index)

    # 3. 填充 System Prompt
    filled_system_prompt = SYSTEM_PROMPT.format(
        emotion_hint=emotion_hint,
        context=context,
        topic_hint=topic_hint,
    )

    # 4. 构建消息列表
    messages = [SystemMessage(content=filled_system_prompt)]

    # 加入历史对话（滑动窗口，控制上下文长度）
    if history:
        recent_history = history[-MAX_HISTORY_TURNS * 2:]
        for msg in recent_history:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
            else:
                role = getattr(msg, "role", "")
                content = getattr(msg, "content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    # 加入当前用户输入（话题发起时为空，不添加空消息）
    if user_input.strip():
        messages.append(HumanMessage(content=user_input))

    # 5. 调用 LLM
    _ensure_initialized()
    response = _llm.invoke(messages)
    return response.content
