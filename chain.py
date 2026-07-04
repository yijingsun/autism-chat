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
        streaming=True,  # 启用流式输出，降低首字延迟
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


def _build_messages(user_input: str, history: list = None, topic_hint: str = "") -> list:
    """
    构建 LLM 消息列表（公共逻辑，供同步/异步调用复用）
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

    return messages


def chat(user_input: str, history: list = None, topic_hint: str = "") -> str:
    """
    处理一轮对话（同步，兼容旧调用）
    """
    _ensure_initialized()
    messages = _build_messages(user_input, history, topic_hint)
    response = _llm.invoke(messages)
    return response.content


async def chat_stream(user_input: str, history: list = None, topic_hint: str = ""):
    """
    流式处理一轮对话，逐 token 推送到 Chainlit 界面

    Args:
        user_input: 用户输入
        history: 对话历史
        topic_hint: 话题引导提示

    Yields:
        每个 token 文本片段
    """
    _ensure_initialized()
    messages = _build_messages(user_input, history, topic_hint) # 构建消息列表

    # 调用链: astream(框架层tracing) → _astream(构造payload) → openai SDK.create() → httpx发送HTTP POST到LLM API
    async for chunk in _llm.astream(messages):
        if chunk.content:
            yield chunk.content
