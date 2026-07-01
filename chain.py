"""
对话链模块
组装 LangChain 对话链：System Prompt + 情绪检测 + RAG + 对话记忆
"""
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import ConversationChain

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
        max_tokens=300,  # 控制回复长度，适合儿童对话
    )


def build_conversation_chain(faiss_index=None) -> ConversationChain:
    """
    构建对话链

    Args:
        faiss_index: FAISS 向量索引（可选，为 None 时 RAG 不生效）

    Returns:
        配置好的 ConversationChain
    """
    llm = get_llm()

    # 使用滑动窗口记忆，控制上下文长度（自闭症儿童对话通常较短）
    memory = ConversationBufferWindowMemory(k=MAX_HISTORY_TURNS)

    # 构建 Prompt 模板
    system_template = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
    human_template = HumanMessagePromptTemplate.from_template("{input}")

    prompt = ChatPromptTemplate.from_messages([system_template, human_template])

    # 组装对话链
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=False,
    )

    # 将 FAISS 索引附加到 chain 上，供后续使用
    chain._faiss_index = faiss_index

    return chain


def chat(user_input: str, chain: ConversationChain) -> str:
    """
    处理一轮对话

    Args:
        user_input: 用户输入
        chain: 对话链实例

    Returns:
        模型回复文本
    """
    # 1. 情绪检测
    emotion = detect_emotion(user_input)
    emotion_hint = EMOTION_HINTS.get(emotion, "")

    # 2. RAG 检索
    faiss_index = getattr(chain, "_faiss_index", None)
    context = retrieve_context(user_input, faiss_index)

    # 3. 调用 LLM
    response = chain.invoke(
        {"input": user_input, "emotion_hint": emotion_hint, "context": context}
    )

    return response["response"]
