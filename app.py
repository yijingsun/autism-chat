"""
主应用入口
基于 Chainlit 构建自闭症友好对话界面

运行方式：
    chainlit run app.py
"""
import chainlit as cl
from chain import init_chain, chat, chat_stream
from rag import load_faiss_index
from prompts import TOPIC_SCENARIOS
from emotion import detect_emotion, get_matched_keywords


# ============================================================
# 初始化
# ============================================================
@cl.on_chat_start
async def on_chat_start():
    """会话开始时初始化系统"""
    print("[启动] 正在初始化系统...", flush=True)
    faiss_index = load_faiss_index()
    init_chain(faiss_index)

    # 欢迎消息 + 话题按钮合并为一条消息，一进来就看到
    actions = [
        cl.Action(name="topic_greetings", label="👋 打招呼", payload={"value": "greetings"}),
        cl.Action(name="topic_emotions", label="😊 认识情绪", payload={"value": "emotions"}),
        cl.Action(name="topic_numbers", label="🔢 数数游戏", payload={"value": "numbers"}),
        cl.Action(name="topic_colors", label="🎨 认颜色", payload={"value": "colors"}),
        cl.Action(name="topic_daily", label="🍎 日常活动", payload={"value": "daily"}),
    ]
    await cl.Message(
        content=(
            "你好呀！我是**星星** 🌟\n\n"
            "我很高兴见到你！😊\n\n"
            "我会用简单的话和你聊天，陪你玩游戏、学新东西。\n"
            "我们可以一起数数、认颜色、聊今天发生了什么有趣的事！\n\n"
            "你想玩什么呢？点下面的按钮吧 👇"
        ),
        author="星星",
        actions=actions,
    ).send()

    print("[启动] 系统初始化完成", flush=True)


# ============================================================
# 话题选择回调（统一处理）
# ============================================================
@cl.action_callback("topic_greetings")
async def on_topic_greetings(action: cl.Action):
    await handle_topic_selection(action)

@cl.action_callback("topic_emotions")
async def on_topic_emotions(action: cl.Action):
    await handle_topic_selection(action)

@cl.action_callback("topic_numbers")
async def on_topic_numbers(action: cl.Action):
    await handle_topic_selection(action)

@cl.action_callback("topic_colors")
async def on_topic_colors(action: cl.Action):
    await handle_topic_selection(action)

@cl.action_callback("topic_daily")
async def on_topic_daily(action: cl.Action):
    await handle_topic_selection(action)


async def handle_topic_selection(action: cl.Action):
    """
    用户点击话题按钮后，由 LLM 主动发起该话题的对话。
    不在界面上显示用户消息，让星星先开口。
    """
    topic_key = action.payload.get("value", "")
    scenario = TOPIC_SCENARIOS.get(topic_key)

    if not scenario:
        return

    topic_prompt = scenario["prompt"]

    # 获取对话历史
    message_history = cl.user_session.get("message_history", [])

    # 流式输出 LLM 回复
    msg = cl.Message(content="", author="星星")
    full_response = ""
    async for token in chat_stream("", message_history, topic_hint=topic_prompt):
        await msg.stream_token(token)
        full_response += token
    await msg.send()

    # 只记录助手的发起消息到历史，不添加虚拟用户消息
    message_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("message_history", message_history)


# ============================================================
# 消息处理
# ============================================================
@cl.on_message
async def on_message(message: cl.Message):
    """处理用户消息"""
    user_input = message.content
    print(f"[DEBUG] 收到消息: '{user_input}'", flush=True)

    if not user_input.strip():
        await cl.Message(content="你好呀！我是星星，我们来聊天吧！", author="星星").send()
        return

    # 情绪检测
    emotion = detect_emotion(user_input)
    keywords = get_matched_keywords(user_input)
    print(f"[情绪检测] 输入: {user_input[:30]}... | 情绪: {emotion} | 关键词: {keywords}", flush=True)

    # 获取对话历史
    message_history = cl.user_session.get("message_history", [])

    # 流式输出 LLM 回复
    msg = cl.Message(content="", author="星星")
    full_response = ""
    async for token in chat_stream(user_input, message_history):
        await msg.stream_token(token)
        full_response += token
    await msg.send()

    # 更新历史
    message_history.append({"role": "user", "content": user_input})
    message_history.append({"role": "assistant", "content": full_response})
    cl.user_session.set("message_history", message_history)
